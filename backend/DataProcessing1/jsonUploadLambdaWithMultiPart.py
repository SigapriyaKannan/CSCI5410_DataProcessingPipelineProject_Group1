import json
import boto3
import os
import uuid
import base64
from requests_toolbelt.multipart import decoder
import time

# Initialize AWS clients
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

# Get environment variables
bucket_name = os.environ['BUCKET_NAME']
glue_trigger_lambda_name = os.environ['GLUE_TRIGGER_LAMBDA_NAME']

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))  # Log the received event

    # Check if the request contains headers
    if 'headers' not in event:
        print("Error: Headers are missing in the request.")
        return {
            'statusCode': 400,
            'body': json.dumps('Headers are missing in the request.')
        }

    # Retrieve the Content-Type header
    content_type = None
    for key in event['headers']:
        if key.lower() == 'content-type':
            content_type = event['headers'][key]
            break

    if content_type is None:
        print("Error: Content-Type header is missing.")
        return {
            'statusCode': 400,
            'body': json.dumps('Content-Type header is missing.')
        }

    if 'multipart/form-data' not in content_type:
        print("Error: Content-Type must be multipart/form-data.")
        return {
            'statusCode': 400,
            'body': json.dumps('Content-Type must be multipart/form-data.')
        }

    # Decode body if necessary
    if event['isBase64Encoded']:
        body = base64.b64decode(event['body'])
    else:
        body = event['body'].encode('utf-8')

    # Parse multipart data
    try:
        multipart_data = decoder.MultipartDecoder(body, content_type)
        print("Multipart data parsed successfully.")
    except Exception as e:
        print(f"Error during multipart parsing: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error during parsing: {str(e)}')
        }

    # Extract fields from the multipart data
    file_content = None
    user_email = None
    role = 'guest'  # Default role

    for part in multipart_data.parts:
        part_headers = {k.decode('utf-8'): v.decode('utf-8') for k, v in part.headers.items()}
        content_disposition = part_headers.get('Content-Disposition', '')
        name = None
        for param in content_disposition.split(';'):
            if 'name' in param:
                name = param.split('=')[1].strip('"')
                break

        if name == 'file':
            file_content = part.content
        elif name == 'email':
            user_email = part.text
        elif name == 'role':
            role = part.text

    # Validate if file is provided
    if file_content is None:
        print("Error: File not provided in the request.")
        return {
            'statusCode': 400,
            'body': json.dumps('File not provided in the request.')
        }

    # Generate unique file name
    user_email = user_email or 'guest'
    file_extension = ".json"
    file_name = f"{user_email}_{uuid.uuid4()}{file_extension}"

    # Upload the file to S3 with metadata
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content,
            Metadata={
                'user_email': user_email,
                'role': role or 'guest'
            }
        )
        print("File uploaded successfully with metadata:", file_name)

        # Confirm file availability in S3 (3 retries with 10s delay)
        for attempt in range(3):
            try:
                s3_client.head_object(Bucket=bucket_name, Key=file_name)
                print(f"File confirmed in S3 on attempt {attempt + 1}")
                break
            except s3_client.exceptions.NoSuchKey:
                time.sleep(10)
        else:
            print("Failed to confirm file availability in S3.")
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to confirm file availability in S3.')
            }

        # Trigger glueTriggerLambda
        response = lambda_client.invoke(
            FunctionName=glue_trigger_lambda_name,
            InvocationType='Event',  # Asynchronous invocation
            Payload=json.dumps({
                's3_input_key': file_name,
                'user_email': user_email,
                'role': role
            })
        )
        print("glueTriggerLambda triggered successfully.")

        return {
            'statusCode': 200,
            'body': json.dumps(f'File uploaded and Glue job triggered successfully: {file_name}')
        }
    except Exception as e:
        print("Error uploading file or triggering Glue job:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error uploading file or triggering Glue job: {str(e)}')
        }
