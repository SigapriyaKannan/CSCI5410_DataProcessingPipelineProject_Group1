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

    # Extract user_email and process_code from the parsed JSON body
    user_email = body.get('user_email')
    process_code = body.get('process_code')

    # Debugging: print user_email and process_code from the parsed body
    print(f"user_email: {user_email}, process_code: {process_code}")

    if not user_email or not process_code:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing user_email or process_code in the request.")
        }

    # Access DynamoDB table
    table = dynamodb.Table(dynamodb_table_name)

    try:
        # Query DynamoDB to retrieve the job status using the user_email and process_code
        response = table.get_item(
            Key={
                'user_email': user_email,
                'process_code': process_code
            }
        )

        # Check if the item exists in DynamoDB
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f'No job found for user {user_email} with process_code {process_code}.')
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

        # Convert the item to JSON serializable format
        serializable_item = decimal_to_float(response['Item'])

        # Return the retrieved item from DynamoDB
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
