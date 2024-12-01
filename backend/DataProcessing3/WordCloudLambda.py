import json
import boto3
import os
import uuid
import base64
import re
import requests
from requests_toolbelt.multipart import decoder
from time import sleep
import time

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
bucket_name = os.environ['BUCKET_NAME']
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
google_function_url = os.environ['GOOGLE_FUNCTION_URL']  # URL of the Google Cloud Function
sns_lambda_url = os.environ['SNS_LAMBDA_URL']  # URL of the SNS Lambda topic


def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))  # Log the received event

    # Check if headers exist and if Content-Type is multipart/form-data
    if 'headers' not in event or 'content-type' not in event['headers']:
        return {"statusCode": 400, "body": json.dumps('Content-Type header is missing or incorrect.')}

    content_type = event['headers']['content-type']

    # Convert content_type to lowercase
    if 'multipart/form-data' not in content_type.lower():
        return {"statusCode": 400, "body": json.dumps('Content-Type must be multipart/form-data.')}

    # Decode body if necessary
    body = base64.b64decode(event['body']) if event['isBase64Encoded'] else event['body'].encode('utf-8')

    # Parse multipart data
    try:
        multipart_data = decoder.MultipartDecoder(body, content_type)
    except Exception as e:
        print(f"Error during multipart parsing: {str(e)}")
        return {"statusCode": 400, "body": json.dumps(f'Error during parsing: {str(e)}')}

    # Extract file content and metadata from multipart form
    file_content, user_email, role = None, 'guest', 'guest'

    for part in multipart_data.parts:
        part_headers = {k.decode('utf-8'): v.decode('utf-8') for k, v in part.headers.items()}
        content_disposition = part_headers.get('Content-Disposition', '')
        if 'name="file"' in content_disposition:
            file_content = part.content
        elif 'name="email"' in content_disposition:
            user_email = part.text
        elif 'name="role"' in content_disposition:
            role = part.text

    if file_content is None:
        return {"statusCode": 400, "body": json.dumps('File not provided in the request.')}

    # Generate a unique .txt filename
    file_name = f"{user_email}_{uuid.uuid4()}.txt"
    looker_url = f"https://lookerstudio.google.com/embed/u/0/reporting/3f0d711f-fff6-4150-9e99-8ddad8228e84/page/4GqLE?user_email_parameter={user_email}"
    iframe = f'<iframe src="{looker_url}" width="100%" height="600" frameborder="0" style="border:0" allowfullscreen></iframe>'

    # Upload the .txt file to S3 with metadata
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content,
            Metadata={'user_email': user_email, 'role': role}
        )

        # Confirm file availability in S3
        for attempt in range(3):
            try:
                s3_client.head_object(Bucket=bucket_name, Key=file_name)
                break
            except s3_client.exceptions.NoSuchKey:
                sleep(10)
        else:
            return {"statusCode": 500, "body": json.dumps('Failed to confirm file availability in S3.')}

    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f'Error uploading file to S3: {str(e)}')}

    # Calculate word frequency from file content for word cloud
    words = re.findall(r'\w+', file_content.decode('utf-8').lower())
    word_frequency = {word: words.count(word) for word in set(words)}

    # Prepare data to send to the Google Cloud Function
    google_function_payload = {
        "user_email": user_email,
        "role": role,
        "filename": file_name,
        "word_frequency": word_frequency
    }

    print(google_function_payload)

    # Invoke Google Cloud Function to write data to Firestore (without Authorization)
    try:
        response = requests.post(google_function_url, json=google_function_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error invoking Google Cloud Function: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f'Error invoking Google Cloud Function: {str(e)}')}

    sns_lambda_payload = {
        "email": user_email,
        "subject": "Data Processing Job has ran successfully",
        "message": f"Your Word Cloud for {file_name} has been generated successfully. You can access it here: {looker_url}"
    }

    print(sns_lambda_payload)

    try:
        response = requests.post(sns_lambda_url, json=sns_lambda_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error invoking Lambda Cloud Function: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f'Error invoking Lambda Cloud Function: {str(e)}')}

    # Save metadata to DynamoDB
    table = dynamodb.Table(dynamodb_table_name)
    metadata = {
        'filename': file_name,
        'file_size': len(file_content),
        'Timestamp': int(time.time()),
        'user_email': user_email,
        'role': role,
        'process_code': str(uuid.uuid4()),
        'Url': looker_url,
        'DownloadUrl': iframe
    }

    try:
        table.put_item(Item=metadata)
    except Exception as e:
        print(f"Error saving metadata to DynamoDB: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f'Error saving metadata to DynamoDB: {str(e)}')}

    print("Data sent to Google Cloud Function and metadata saved to DynamoDB.")

    return {"statusCode": 200, "body": json.dumps(f'File uploaded and data processed for {file_name}')}
