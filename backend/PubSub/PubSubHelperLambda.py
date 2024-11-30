import json
import boto3
import os
import requests

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Environment variables
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
second_table_name = os.environ['SECOND_DYNAMODB_TABLE_NAME']
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

    # Query DynamoDB tables
    items = []  # Initialize an empty list to hold data from both tables
    found_in_either = False  # Flag to track if the email is found in at least one table

    try:
        # Query the first table
        table1 = dynamodb.Table(dynamodb_table_name)
        response1 = table1.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(email)
        )
        table1_items = response1.get('Items', [])
        if table1_items:
            found_in_either = True
            items.extend(table1_items)  # Append data from the first table

        # Query the second table
        table2 = dynamodb.Table(second_table_name)
        response2 = table2.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(email)
        )
        table2_items = response2.get('Items', [])
        if table2_items:
            found_in_either = True
            items.extend(table2_items)  # Append data from the second table
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": f"DynamoDB query error: {str(e)}"})}

    # Check if the email was not found in either table
    if not found_in_either:
        return {"statusCode": 404, "body": json.dumps({"error": "No data found for the provided email in either table"})}

    # Prepare data for GCP Cloud Function
    gcp_payload = {
        "user_email": email,
        "role": role,
        "data": items  # Includes data from both tables without altering schema
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
