import json
import boto3
import os
import time
from botocore.exceptions import ClientError

# Initialize AWS clients
glue_client = boto3.client('glue')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
glue_job_name = os.environ['GLUE_JOB_NAME']

# Global variable to store user email
user_email = None
process_code = None

def lambda_handler(event, context):
    global user_email
    global process_code

    print("Received event:", json.dumps(event, indent=2))

    try:
        # Extract details from the event
        s3_key = event['s3_input_key']
        user_email = event['user_email']  # Assign the email globally
        role = event.get('role', 'guest')  # Default role
        process_code = event['process_code']

        print(f"Starting Glue job with Job ID: {process_code}, User: {user_email}, Role: {role}")

        # Save the initial RUNNING status in DynamoDB
        save_initial_status_to_dynamodb(process_code, s3_key)

        # Start the Glue job
        response = glue_client.start_job_run(
            JobName=glue_job_name,
            Arguments={
                '--s3_input_key': s3_key,
                '--dynamodb_table_name': dynamodb_table_name,
                '--bucket_name': os.environ['BUCKET_NAME'],
                '--user_email': user_email,
                '--role': role,
                '--new_bucket_name': os.environ['NEW_BUCKET_NAME'],
                '--process_code':process_code
            }
        )
        job_run_id = response['JobRunId']
        print(f"Started Glue job {glue_job_name}: {job_run_id}")

        # Update DynamoDB with the Glue JobRunId
        update_job_run_id_in_dynamodb(process_code, job_run_id)

        # Poll the Glue job status until it finishes or times out
        job_status = monitor_glue_job(glue_job_name, job_run_id)

        # Update the final job status in DynamoDB
        update_job_status_in_dynamodb(process_code, job_status)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Glue job completed successfully.',
                'process_code': process_code,
                'final_status': job_status
            })
        }
    except Exception as e:
        print(f"Error in GlueTriggerLambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error in GlueTriggerLambda: {str(e)}')
        }

def save_initial_status_to_dynamodb(process_code, s3_key):
    """
    Save the initial job metadata and status to DynamoDB.
    """
    global user_email  # Use global email
    table = dynamodb.Table(dynamodb_table_name)
    try:
        table.put_item(
            Item={
                'user_email': user_email,
                'process_code': process_code,
                'JobStatus': 'RUNNING',
                'S3JsonFilePath': s3_key,
                'Timestamp': int(time.time())
            }
        )
        print(f"Initial job status saved for Job ID: {process_code}")
    except ClientError as e:
        print(f"Error saving initial status to DynamoDB: {e.response['Error']['Message']}")

def update_job_run_id_in_dynamodb(process_code, job_run_id):
    """
    Update the Glue JobRunId in DynamoDB.
    """
    global user_email  # Use global email
    table = dynamodb.Table(dynamodb_table_name)
    try:
        table.update_item(
            Key={'user_email': user_email, 'process_code': process_code},
            UpdateExpression="SET JobRunId = :job_run_id",
            ExpressionAttributeValues={
                ':job_run_id': job_run_id
            }
        )
        print(f"Glue JobRunId updated in DynamoDB for Job ID: {process_code}")
    except ClientError as e:
        print(f"Error updating JobRunId in DynamoDB: {e.response['Error']['Message']}")

def monitor_glue_job(glue_job_name, job_run_id):
    """
    Monitor the Glue job status for up to 10 minutes (600 seconds).
    """
    timeout = 600  # Timeout in seconds
    interval = 60  # Poll every 60 seconds

    for _ in range(timeout // interval):
        job_run = glue_client.get_job_run(JobName=glue_job_name, RunId=job_run_id)
        job_status = job_run['JobRun']['JobRunState']
        print(f"Job status: {job_status}")

        if job_status in ['SUCCEEDED', 'FAILED', 'STOPPED']:
            return job_status
        time.sleep(interval)

    # If timeout is reached, return a timeout status
    print(f"Glue job {glue_job_name} timed out.")
    return 'TIMEOUT'

def update_job_status_in_dynamodb(process_code, final_status):
    """
    Update the final Glue job status in DynamoDB.
    """
    global user_email  # Use global email
    table = dynamodb.Table(dynamodb_table_name)
    try:
        table.update_item(
            Key={'user_email': user_email, 'process_code': process_code},
            UpdateExpression="SET JobStatus = :final_status",
            ExpressionAttributeValues={
                ':final_status': final_status
            }
        )
        print(f"Final status updated to {final_status} for Job ID: {process_code}")
    except ClientError as e:
        print(f"Error updating final status in DynamoDB: {e.response['Error']['Message']}")
