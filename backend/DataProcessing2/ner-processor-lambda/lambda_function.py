import json
import time
import os
import boto3
import spacy
import uuid
import base64
import requests
from requests_toolbelt.multipart import decoder

nlp = spacy.load("en_core_web_sm")

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
bucket_name = os.environ['S3_BUCKET_NAME']
processed_bucket_name = os.environ['S3_PROCESSED_BUCKET_NAME']

def lambda_handler(event, context):
    try:
        if event['isBase64Encoded']:
            body = base64.b64decode(event['body'])
        else:
            body = event['body']

        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type', '')
        multipart_data = decoder.MultipartDecoder(body, content_type)
        
        fields = {
            part.headers[b'Content-Disposition'].decode().split(';')[1].split('=')[1].strip('"'): part.content.decode()
            for part in multipart_data.parts if b'Content-Disposition' in part.headers
        }
        files = [
            part for part in multipart_data.parts
            if b'Content-Disposition' in part.headers and 'filename' in part.headers[b'Content-Disposition'].decode()
        ]

        email = fields.get('email')
        if not email:
            return cors_response(400, {'error': 'Missing email.'})

        file_content = files[0].content.decode() if files else None
        if not file_content:
            return cors_response(400, {'error': 'File content is empty or invalid.'})

        file_id = str(uuid.uuid4())
        s3_key_original = f'uploads/{file_id}.txt'
        s3_key_processed = f'entities/{file_id}_processed.json'

        try:
            s3_client.put_object(Bucket=bucket_name, Key=s3_key_original, Body=file_content)
        except Exception as s3_error:
            return cors_response(500, {'error': 'Failed to upload file to S3.', 'details': str(s3_error)})

        doc = nlp(file_content)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

        if not entities:
            notify_user(email, "NER Processing Failed", f"Hello, your file ID: {file_id} could not be processed due to no extractable entities.")
            return cors_response(400, {'error': 'No entities extracted from the file.'})

        entities_json = json.dumps(entities, indent=4)

        try:
            s3_client.put_object(Bucket=processed_bucket_name, Key=s3_key_processed, Body=entities_json)
        except Exception as s3_error:
            notify_user(email, "NER Processing Failed", f"Hello, your file ID: {file_id} could not be processed due to a storage issue.")
            return cors_response(500, {'error': 'Failed to upload entities file to S3.', 'details': str(s3_error)})

        original_file_url = f"https://{bucket_name}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{s3_key_original}"
        processed_file_url = f"https://{processed_bucket_name}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{s3_key_processed}"

        try:
            table.put_item(
                Item={
                    'reference_code': file_id,
                    'user_email': email,
                    'original_file_s3_location': original_file_url,
                    'processed_file_s3_location': processed_file_url,
                    'timestamp': int(time.time()),
                    'job_status': 'SUCCEEDED',
                    'extracted_entities': entities,
                }
            )
        except Exception as db_error:
            notify_user(email, "NER Processing Failed", f"Hello, your file ID: {file_id} could not be processed due to a database error.")
            return cors_response(500, {'error': 'Failed to save data to DynamoDB.', 'details': str(db_error)})

        notify_user(email, "NER Processing Success", f"Hello, your file ID: {file_id} was processed successfully. Processed data is available at {processed_file_url}")

        return cors_response(200, {
            'reference_code': file_id,
            'processed_file_s3_location': processed_file_url,
            'timestamp': int(time.time()),
            'job_status': 'SUCCEEDED',
            'extracted_entities': entities
        })

    except Exception as e:
        return cors_response(500, {'error': 'Internal server error', 'details': str(e)})

def cors_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Authorization, Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'body': json.dumps(body)
    }
    
def notify_user(email, subject, message):
    api_url = "https://4felas5im2setdsipr3dryjdhi0jeauv.lambda-url.us-east-1.on.aws/"
    payload = {
        "email": email,
        "subject": subject,
        "message": message
    }
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send email notification: {response.text}")
    except Exception as e:
        print(f"Error occurred while sending email: {str(e)}")
