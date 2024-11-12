import json
import boto3
import os
import time
import uuid

# Initialize AWS clients
glue_client = boto3.client('glue')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
glue_job_name = os.environ['GLUE_JOB_NAME']
bucket_name = os.environ['BUCKET_NAME']  # Add bucket name from environment variable

def lambda_handler(event, context):
    global user_email
    print("Received event:", json.dumps(event, indent=2))  # Log the event for debugging

    # Extract details directly from the event
    try:
        s3_key = event['s3_input_key']
        print(s3_key)
        user_email = event.get('user_email', 'guest')
        print(user_email)  # Default to 'guest' if not provided
        role = event.get('role', 'guest')
        print(role)  # Default to 'guest' if not provided
    except KeyError as e:
        print(f"Missing key in the event: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Missing key in the event: {str(e)}')
        }

    # Start the Glue job
    try:
        response = glue_client.start_job_run(
            JobName=glue_job_name,
            Arguments={
                '--s3_input_key': s3_key,
                '--dynamodb_table_name': dynamodb_table_name,
                '--bucket_name': bucket_name,  # Pass the bucket name to the Glue job
                '--user_email': user_email,
                '--role': role
            }
        )
        job_run_id = response['JobRunId']
        print(f"Started Glue job {glue_job_name}: {job_run_id}")

        # Wait for the Glue job to complete (with a timeout)
        timeout = 600  # Set your timeout (in seconds)
        interval = 60   # Check every 60 seconds

        for _ in range(timeout // interval):
            job_run = glue_client.get_job_run(JobName=glue_job_name, RunId=job_run_id)
            job_status = job_run['JobRun']['JobRunState']
            if job_status in ['SUCCEEDED', 'FAILED', 'STOPPED']:
                break
            time.sleep(interval)

        # Check job status and save to DynamoDB only if succeeded
        if job_status == 'SUCCEEDED':
            save_status_to_dynamodb(
                job_name=glue_job_name,
                job_run_id=job_run_id,
                status=job_status,
                s3_key=s3_key
            )
        else:
            print(f"Glue job {glue_job_name} did not succeed. Status: {job_status}")

        return {
            'statusCode': 200,
            'body': json.dumps(f'Glue job {glue_job_name} triggered successfully with run ID {job_run_id}!')
        }
    except Exception as e:
        print(f"Error starting Glue job {glue_job_name}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error starting Glue job {glue_job_name}: {str(e)}')
        }

def save_status_to_dynamodb(job_name, job_run_id, status, s3_key):
    """
    Save the status and metadata of the Glue job to DynamoDB.
    This function appends the job status to the 'JobStatusHistory' list in DynamoDB.
    If the list doesn't exist, it creates a new one.

    """
    table = dynamodb.Table(dynamodb_table_name)

    try:

        response = table.update_item(
            Key={'user_email': user_email},
            UpdateExpression="SET #job_status_history = list_append(if_not_exists(#job_status_history, :empty_list), :new_status)",
            ExpressionAttributeNames={
                '#job_status_history': 'JobStatusHistory',
            },
            ExpressionAttributeValues={
                ':new_status': [{
                    'JobRunId': job_run_id,
                    'JobStatus': status,
                    'S3JsonFilePath': s3_key,
                    'Timestamp': int(time.time())
                }],
                ':empty_list': []  # Initialize the list if it doesn't exist
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Appended job status to DynamoDB for user {user_email}.")
    except Exception as e:
        print(f"Error saving status to DynamoDB: {str(e)}")
