from google.cloud import firestore
import json

# Firestore client
db = firestore.Client()


def get_process_codes(request):
    """Fetch all process codes for a given user."""
    try:
        # Log the initial request for debugging
        print(f"Received request: {request}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {request.headers}")

        # Handling CORS preflight request (OPTIONS)
        if request.method == 'OPTIONS':
            headers = {
                "Access-Control-Allow-Origin": "*",  # Allow all origins or specify your frontend URL
                "Access-Control-Allow-Methods": "POST, OPTIONS",  # Allow POST and OPTIONS methods
                "Access-Control-Allow-Headers": "Content-Type",  # Allow Content-Type header
                "Access-Control-Max-Age": "3600",  # Cache preflight response for 1 hour
            }
            print(f"Preflight CORS headers: {headers}")  # Debugging: check preflight headers
            return ('', 204, headers)

        # Set CORS headers for the main POST request
        headers = {
            "Access-Control-Allow-Origin": "*"
            # Allow all origins (you can replace "*" with your frontend URL for better security)
        }
        print(f"Response CORS headers: {headers}")  # Debugging: check response headers

        # Parse the request JSON
        request_json = request.get_json()
        if not request_json:
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        user_email = request_json.get('user_email')
        if not user_email:
            return json.dumps({'error': 'Missing required field: user_email'}), 400, headers

        # Fetch pubsub_data document for the given user
        pubsub_ref = db.collection('pubsub_data').document(user_email)
        pubsub_doc = pubsub_ref.get()

        if not pubsub_doc.exists:
            return json.dumps({'error': 'No process codes found for the given user_email'}), 404, headers

        # Extract process codes from the document
        pubsub_data = pubsub_doc.to_dict()
        process_codes = list(pubsub_data.get('process_codes', {}).keys())

        print(f"Found process codes for {user_email}: {process_codes}")  # Debugging: check process codes

        return json.dumps({'codes': process_codes}), 200, headers

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)  # Debugging: log the error
        return json.dumps({'error': error_message}), 500, headers
