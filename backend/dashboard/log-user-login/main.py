import functions_framework
from google.cloud import bigquery
from datetime import datetime, timezone

@functions_framework.http
def log_user_login(request):
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)

    # Only allow POST requests
    if request.method != 'POST':
        return 'Method not allowed', 405

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }

    if not request.json.get('user_id'):
        return 'user id not found', 400
    if not request.json.get('user_type'):
        return 'user type not found', 400
    
    bq_client = bigquery.Client()

    login_data = {
        'user_id': request.json.get('user_id'),
        'user_type': request.json.get('user_type'),
        'login_timestamp': datetime.now(timezone.utc).isoformat(),
        'login_date': datetime.now(timezone.utc).date().isoformat()
    }
    
    table_id = 'k8s-assignment-csci5409.QuickDataPro.user_logins'
    
    try:
        errors = bq_client.insert_rows_json(table_id, [login_data])
        if errors:
            print(f"Errors inserting data: {errors}")
            return 'Error inserting data', 500
        
        return 'Login logged successfully', 200, headers
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return f'Error: {str(e)}', 500
