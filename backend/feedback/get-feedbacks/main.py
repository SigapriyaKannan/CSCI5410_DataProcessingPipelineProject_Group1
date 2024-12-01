import functions_framework
from google.cloud import firestore
import json

@functions_framework.http
def get_feedback_sentiments(request):
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        return ('', 204, headers)

    # Only allow GET requests
    if request.method != 'GET':
        return 'Method not allowed', 405

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }

    try:
        # Initialize Firestore client
        firestore_client = firestore.Client()
        
        # Get feature from query parameter
        feature = request.args.get('feature')
        
        # Retrieve feedback sentiments
        sentiments_ref = firestore_client.collection('feedback-sentiments')
        
        # Apply feature filter if provided
        if feature:
            sentiments_query = sentiments_ref.where('feature', '==', feature)
            sentiments = sentiments_query.stream()
        else:
            sentiments = sentiments_ref.stream()
        
        # Convert to list of dictionaries
        feedback_list = []
        for doc in sentiments:
            sentiment_dict = doc.to_dict()
            sentiment_dict['id'] = doc.id
            feedback_list.append(sentiment_dict)
        
        # Sort by timestamp (most recent first)
        feedback_list.sort(key=lambda x: x['timestamp'], reverse=True)

        # Return JSON response
        return json.dumps(feedback_list), 200, headers

    except Exception as e:
        return f'Error retrieving sentiments: {str(e)}', 500
        