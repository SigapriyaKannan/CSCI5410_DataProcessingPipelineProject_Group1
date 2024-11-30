import json
import boto3
import os
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Get environment variables
dynamodb_table_name = os.environ.get('DYNAMODB_TABLE_NAME')


def lambda_handler(event, context):
    # Debugging: print the incoming event to understand its structure
    print("Event:", json.dumps(event, indent=2))

    # Parse the body of the event (it is a JSON string)
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format in the request body.')
        }

    # Extract user_email from the parsed JSON body
    user_email = body.get('user_email')

    # Debugging: print user_email from the parsed body
    print(f"user_email: {user_email}")

    if not user_email:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing user_email in the request.")
        }

    # Access DynamoDB table
    table = dynamodb.Table(dynamodb_table_name)

    try:
        # Query DynamoDB to retrieve the job status using the user_email
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(user_email)
        )

        # Check if any items exist in DynamoDB for the given user_email
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps(f'No jobs found for user {user_email}.')
            }

        # Convert any Decimal objects to float or int for JSON serialization
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: decimal_to_float(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            else:
                return obj

        # Extract and filter the required fields for all jobs

        filtered_items = [
            {
                'filename': item.get('filename'),
                'file_size': item.get('file_size'),
                'Timestamp': item.get('Timestamp'),
                'process_code': item.get('process_code'),
                'Url': item.get('Url'),
                'DownloadUrl': item.get('DownloadUrl')

            }
            for item in response['Items']
        ]

        # Convert the filtered items to a JSON serializable format
        serializable_items = decimal_to_float(filtered_items)

        # Return the filtered items
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
