import json
import os
import boto3
import spacy
import uuid
import base64
from requests_toolbelt.multipart import decoder

# Load the SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Initialize S3 and DynamoDB clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
bucket_name = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    try:
        # Ensure the request body is base64-encoded
        if event['isBase64Encoded']:
            body = base64.b64decode(event['body'])
        else:
            body = event['body']

        # Parse the multipart form-data
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type', '')
        multipart_data = decoder.MultipartDecoder(body, content_type)
        
        # Extract fields from form-data
        fields = {
            part.headers[b'Content-Disposition'].decode().split(';')[1].split('=')[1].strip('"'): part.content.decode()
            for part in multipart_data.parts if b'Content-Disposition' in part.headers
        }
        files = [
            part for part in multipart_data.parts
            if b'Content-Disposition' in part.headers and 'filename' in part.headers[b'Content-Disposition'].decode()
        ]

        # Validate email and file content
        email = fields.get('email')
        if not email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing email.'})
            }

        file_content = files[0].content.decode() if files else None
        if not file_content:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'File content is empty or invalid.'})
            }

        # Create a unique file ID and S3 object key
        file_id = str(uuid.uuid4())
        s3_key = f'uploads/{file_id}.txt'

        # Upload the file content to S3
        try:
            s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=file_content)
        except Exception as s3_error:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to upload file to S3.', 'details': str(s3_error)})
            }

        # Process the text with SpaCy to extract named entities
        doc = nlp(file_content)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

        # Store entities and metadata in DynamoDB
        try:
            table.put_item(
                Item={
                    'reference_code': file_id,
                    'user_email': email,
                    's3_location': f's3://{bucket_name}/{s3_key}',
                    'extracted_entities': entities,
                }
            )
        except Exception as db_error:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to save data to DynamoDB.', 'details': str(db_error)})
            }

        # Return the extracted entities and file location as a JSON response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'reference_code': file_id,
                's3_location': f's3://{bucket_name}/{s3_key}',
                'extracted_entities': entities
            })
        }

    except Exception as e:
        # Catch any unexpected exceptions and return a server error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }
