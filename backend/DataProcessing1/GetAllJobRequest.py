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

    print(f"user_email: {user_email}")

    if not user_email:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing user_email in the request.")
        }

    table = dynamodb.Table(dynamodb_table_name)

    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(user_email)
        )

        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps(f'No jobs found for user {user_email}.')
            }

        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: decimal_to_float(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            else:
                return obj

        filtered_items = [
            {
                'JobStatus': item.get('JobStatus'),
                'filename': item.get('S3JsonFilePath'),
                'ProcessedFile': item.get('S3CsvFilePath'),
                'Timestamp': item.get('Timestamp'),
                'RowCount': item.get('RowCount'),
                'process_code': item.get('process_code')
            }
            for item in response['Items']
        ]

        serializable_items = decimal_to_float(filtered_items)

        return {
            'statusCode': 200,
            'body': json.dumps(serializable_items)
        }

    except ClientError as e:
        print(f"Error querying DynamoDB: {e.response['Error']['Message']}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error querying DynamoDB: {e.response['Error']['Message']}")
        }
