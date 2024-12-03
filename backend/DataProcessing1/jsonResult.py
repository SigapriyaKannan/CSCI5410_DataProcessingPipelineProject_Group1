import json
import boto3
import os
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

dynamodb_table_name = os.environ.get('DYNAMODB_TABLE_NAME')


def lambda_handler(event, context):
    print("Event:", json.dumps(event, indent=2))

    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format in the request body.')
        }

    user_email = body.get('user_email')
    process_code = body.get('process_code')

    print(f"user_email: {user_email}, process_code: {process_code}")

    if not user_email or not process_code:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing user_email or process_code in the request.")
        }

    table = dynamodb.Table(dynamodb_table_name)

    try:
        response = table.get_item(
            Key={
                'user_email': user_email,
                'process_code': process_code
            }
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f'No job found for user {user_email} with process_code {process_code}.')
            }

        job_item = response['Item']

        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: decimal_to_float(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            else:
                return obj

        filtered_item = {
            'JobStatus': job_item.get('JobStatus'),
            'processed_file_name': job_item.get('processed_file_name'),
            'S3CsvFilePath': job_item.get('S3CsvFilePath'),
            'S3JsonFilePath': job_item.get('S3JsonFilePath')
        }

        serializable_item = decimal_to_float(filtered_item)

        return {
            'statusCode': 200,
            'body': json.dumps(serializable_item)
        }

    except ClientError as e:
        print(f"Error querying DynamoDB: {e.response['Error']['Message']}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error querying DynamoDB: {e.response['Error']['Message']}")
        }
