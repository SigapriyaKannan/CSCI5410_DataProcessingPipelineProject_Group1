import functions_framework
from google.cloud import storage
import json
import uuid
from datetime import datetime

@functions_framework.http
def store_feedback(request):
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

    try:
        # Parse request data
        request_json = request.get_json(silent=True)
        feedback = request_json.get('feedback')
        feature = request_json.get('feature')

        if not feedback:
            return 'No feedback provided', 400
        if not feature:
            return 'No feature provided', 400

        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket('feedback-bucket-2804')

        # Generate unique filename
        filename = f"feedback_{uuid.uuid4()}_{datetime.now().isoformat()}.json"
        blob = bucket.blob(filename)

        # Store feedback as JSON (timestamp generated here)
        feedback_data = {
            'feedback': feedback,
            'feature': feature,
            'timestamp': datetime.now().isoformat()
        }
        blob.upload_from_string(
            data=json.dumps(feedback_data),
            content_type='application/json'
        )

        return ('Feedback stored successfully', 200, headers)

    except Exception as e:
        return f'Error storing feedback: {str(e)}', 500
