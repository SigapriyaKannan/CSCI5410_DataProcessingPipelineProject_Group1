from google.cloud import firestore
import json

# Firestore client
db = firestore.Client()

def get_agent_conversations(request):
    """Fetch all conversations assigned to a specific agent."""
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
            "Access-Control-Allow-Origin": "*"  # Allow all origins (you can replace "*" with your frontend URL for better security)
        }
        print(f"Response CORS headers: {headers}")  # Debugging: check response headers

        # Parse the request JSON
        request_json = request.get_json()
        if not request_json:
            print("Error: Missing request body")  # Debugging statement
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        agent_email = request_json.get('agent_email')
        if not agent_email:
            print("Error: Missing agent_email field")  # Debugging statement
            return json.dumps({'error': 'Missing required field: agent_email'}), 400, headers

        print(f"Fetching conversations assigned to agent: {agent_email}")  # Debugging statement

        # Query Firestore for conversations assigned to the agent
        conversations_ref = db.collection('conversations').where('assigned_agent', '==', agent_email).stream()

        # Extract process codes from the matching conversations
        process_codes = [doc.id for doc in conversations_ref]

        if not process_codes:
            print(f"No assigned conversations found for agent: {agent_email}")  # Debugging statement
            return json.dumps({'message': 'No assigned conversations found for the agent'}), 404, headers

        print(f"Found conversations for agent {agent_email}: {process_codes}")  # Debugging statement

        return json.dumps({'conversations': process_codes}), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging statement
        return json.dumps({'error': str(e)}), 500, headers
