import json
import boto3
import os
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    try:
        # Extract email directly from the event object
        body = json.loads(event.get('body', '{}'))
        email = body.get('user_email')
        if not email:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Email parameter is required.'}),
            }
        
        # Query DynamoDB for records with the given email
        response = table.query(
            IndexName='user_email-index',  # Ensure a GSI is created on 'user_email' for querying
            KeyConditionExpression=Key('user_email').eq(email),
        )
        
        # Extract processed file details from the response
        items = response.get('Items', [])
        processed_file_details = [
            {
                'reference_code': item['reference_code'],
                'processed_file_s3_location': item.get('processed_file_s3_location'),
                'job_status': item.get('job_status'),
            }
            for item in items
        ]

        # Return the processed file details as JSON
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': json.dumps({
                'user_email': email,
                'file_locations': processed_file_details,
            }),
        }

    except Exception as e:
        # Catch any unexpected exceptions and return a server error
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)}),
        }
