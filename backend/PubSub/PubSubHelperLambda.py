import json
import boto3
import os
import requests

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Environment variables
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
google_function_url = os.environ['GOOGLE_FUNCTION_URL']

def lambda_handler(event, context):
    try:
        # Parse the request body
        request = json.loads(event['body'])
        email = request['email']  # Partition key
        role = request['role']  # Role to validate access
    except (KeyError, ValueError) as e:
        return {"statusCode": 400, "body": json.dumps({"error": f"Invalid input: {str(e)}"})}

    # Validate role
    if role.lower() == "agent":
        return {"statusCode": 403, "body": json.dumps({"error": "Access denied: Role not permitted"})}

    # Query DynamoDB for all records associated with the email
    try:
        table = dynamodb.Table(dynamodb_table_name)
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(email)
        )
        items = response.get('Items', [])

        if not items:
            return {"statusCode": 404, "body": json.dumps({"error": "No data found for the provided email"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": f"DynamoDB query error: {str(e)}"})}

    # Prepare data for GCP Cloud Function
    gcp_payload = {
        "user_email": email,
        "role": role,
        "data": items  # Includes all records with process_code
    }

    # Send the data to the GCP Cloud Function
    try:
        response = requests.post(google_function_url, json=gcp_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error invoking Google Cloud Function: {str(e)}"})
        }

    # Return success response
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Data successfully sent to GCP Cloud Function",
            "response": response.json()
        })
    }
