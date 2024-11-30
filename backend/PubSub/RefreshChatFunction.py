from google.cloud import firestore
import json

# Firestore client
db = firestore.Client()


def fetch_chat_messages(request):
    """Fetch all messages for a given process_code when the refresh button is clicked."""
    try:
        # CORS configuration for handling OPTIONS preflight request
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

        # Parse incoming request JSON
        request_json = request.get_json()
        if not request_json:
            print("Error: Missing request body")  # Debugging statement
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        process_code = request_json.get('process_code')
        if not process_code:
            print("Error: Missing process_code")  # Debugging statement
            return json.dumps({'error': 'Missing required field: process_code'}), 400, headers

        print(f"Fetching conversation for process_code: {process_code}")  # Debugging statement

        # Fetch the conversation document using process_code
        conversation_ref = db.collection('conversations').document(process_code)
        conversation_doc = conversation_ref.get()

        if not conversation_doc.exists:
            print(f"Error: Conversation not found for process_code: {process_code}")  # Debugging statement
            return json.dumps({'error': 'Conversation not found for the provided process_code'}), 404, headers

        # Retrieve the messages from the conversation document
        conversation_data = conversation_doc.to_dict()
        messages = conversation_data.get('messages', [])

        print(f"Retrieved messages for process_code {process_code}: {messages}")  # Debugging statement

        # Return the messages to the frontend
        return json.dumps({
            'message': 'Chat fetched successfully',
            'messages': messages
        }), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging statement
        return json.dumps({'error': str(e)}), 500, headers
