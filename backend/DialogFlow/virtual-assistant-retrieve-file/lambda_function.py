import json
import requests
import os

API_URLS = [
    os.environ['API_URL_1'],  
    os.environ['API_URL_2'],  
    os.environ['API_URL_3'],  
]

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        process_code = body.get('process_code')
        user_email = body.get('user_email')

        if not process_code or not user_email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'process_code and user_email are required.'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                }
            }

        for api_url in API_URLS:
            response = requests.post(
                api_url,
                json={'user_email': user_email},
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                continue  

            data = response.json()

            if api_url == os.environ['API_URL_1']:
                for file in data:
                    if file.get('process_code') == process_code and file.get('JobStatus') == "SUCCEEDED":
                        return {
                            'statusCode': 200,
                            'body': json.dumps({
                                'process_code': process_code,
                                'processed_file_url': file.get('ProcessedFile', 'No file available'),
                            }),
                            'headers': {
                                'Access-Control-Allow-Origin': '*',  
                                'Access-Control-Allow-Headers': 'Content-Type',
                                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                            }
                        }

            elif api_url == os.environ['API_URL_2']:
                for file in data:
                    if file.get('process_code') == process_code:
                        return {
                            'statusCode': 200,
                            'body': json.dumps({
                                'process_code': process_code,
                                'processed_file_url': file.get('Url', 'No file available'),
                                'download_url': file.get('DownloadUrl', 'No download URL available'),
                            }),
                            'headers': {
                                'Access-Control-Allow-Origin': '*', 
                                'Access-Control-Allow-Headers': 'Content-Type',
                                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                            }
                        }

            elif api_url == os.environ['API_URL_3']:
                for file in data.get('file_locations', []):
                    if file.get('reference_code') == process_code and file.get('job_status') == "SUCCEEDED":
                        return {
                            'statusCode': 200,
                            'body': json.dumps({
                                'process_code': process_code,
                                'processed_file_url': file.get('processed_file_s3_location'),
                            }),
                            'headers': {
                                'Access-Control-Allow-Origin': '*', 
                                'Access-Control-Allow-Headers': 'Content-Type',
                                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                            }
                        }

        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'No file found for process_code: {process_code}.'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
