import json
import boto3
import os
import requests

dynamodb = boto3.resource('dynamodb')

dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
second_table_name = os.environ['SECOND_DYNAMODB_TABLE_NAME']
google_function_url = os.environ['GOOGLE_FUNCTION_URL']

def lambda_handler(event, context):
    try:
        request = json.loads(event['body'])
        email = request['email']
        role = request['role']
    except (KeyError, ValueError) as e:
        return {"statusCode": 400, "body": json.dumps({"error": f"Invalid input: {str(e)}"})}

    if role.lower() == "agent":
        return {"statusCode": 403, "body": json.dumps({"error": "Access denied: Role not permitted"})}

    items = []
    found_in_either = False

    try:
        table1 = dynamodb.Table(dynamodb_table_name)
        response1 = table1.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(email)
        )
        table1_items = response1.get('Items', [])
        if table1_items:
            found_in_either = True
            items.extend(table1_items)

        table2 = dynamodb.Table(second_table_name)
        response2 = table2.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(email)
        )
        table2_items = response2.get('Items', [])
        if table2_items:
            found_in_either = True
            items.extend(table2_items)
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": f"DynamoDB query error: {str(e)}"})}

    if not found_in_either:
        return {"statusCode": 404, "body": json.dumps({"error": "No data found for the provided email in either table"})}

    gcp_payload = {
        "user_email": email,
        "role": role,
        "data": items
    }

    try:
        response = requests.post(google_function_url, json=gcp_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error invoking Google Cloud Function: {str(e)}"})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Data successfully sent to GCP Cloud Function",
            "response": response.json()
        })
    }
