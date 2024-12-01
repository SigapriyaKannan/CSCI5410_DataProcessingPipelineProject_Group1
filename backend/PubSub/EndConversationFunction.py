from google.cloud import firestore
import json

# Firestore client
db = firestore.Client()

def end_conversation(request):
    """Endpoint to end a conversation based on user or agent request."""
    try:
        # Log the incoming request for debugging
        print(f"Received request: {request}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {request.headers}")

        # Handle CORS preflight request (OPTIONS)
        if request.method == 'OPTIONS':
            headers = {
                "Access-Control-Allow-Origin": "*",  # Allow all origins or specify your frontend URL
                "Access-Control-Allow-Methods": "POST, OPTIONS",  # Allow POST and OPTIONS methods
                "Access-Control-Allow-Headers": "Content-Type",  # Allow Content-Type header
                "Access-Control-Max-Age": "3600",  # Cache preflight response for 1 hour
            }
            print(f"Preflight CORS headers: {headers}")  # Debugging: log headers
            return ('', 204, headers)

        # Set CORS headers for the main POST request
        headers = {
            "Access-Control-Allow-Origin": "*",  # Allow all origins (or replace "*" with your frontend URL for better security)
        }
        print(f"Response CORS headers: {headers}")  # Debugging: log headers

        # Parse incoming JSON request
        request_json = request.get_json()
        if not request_json:
            print("Error: Missing JSON body")  # Debugging statement
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        process_code = request_json.get('process_code')
        role = request_json.get('role')
        status = request_json.get('status')  # "yes" or "no"

        # Log parsed fields for debugging
        print(f"Parsed data - process_code: {process_code}, role: {role}, status: {status}")  # Debugging statement

        # Validate input fields
        if not all([process_code, role, status]):
            print("Error: Missing required fields")  # Debugging statement
            return json.dumps({'error': 'Missing required fields: process_code, role, and status'}), 400, headers

        # Validate status value
        if status not in ["yes", "no"]:
            print("Error: Invalid status value")  # Debugging statement
            return json.dumps({'error': 'Invalid status value. It should be "yes" or "no".'}), 400, headers

        # Fetch the conversation based on the process code
        conversation_ref = db.collection('conversations').document(process_code)
        conversation_doc = conversation_ref.get()

        if not conversation_doc.exists:
            print(f"Error: Conversation not found for process_code: {process_code}")  # Debugging statement
            return json.dumps({'error': 'Conversation not found for the provided process_code'}), 404, headers

        # Handle agent requests
        if role == "agent":
            # If the status is "yes", mark the conversation as resolved and delete it
            if status == "yes":
                print(f"Marking conversation as resolved and deleting for process_code: {process_code}")  # Debugging statement
                conversation_ref.update({
                    "assigned_agent": None,  # Unassign the agent
                    "status": "resolved"     # Optionally mark as resolved
                })
                conversation_ref.delete()  # Delete the conversation document
                return json.dumps({'message': 'Conversation resolved, agent unassigned, and conversation deleted.'}), 200, headers
            elif status == "no":
                print(f"Conversation not resolved. Agent remains assigned for process_code: {process_code}")  # Debugging statement
                return json.dumps({'message': 'Conversation not resolved. Agent remains assigned.'}), 200, headers

        # Handle user requests
        elif role == "user":
            # If the status is "yes", mark the conversation as closed and delete it
            if status == "yes":
                print(f"Closing conversation and deleting for process_code: {process_code}")  # Debugging statement
                conversation_ref.update({
                    "status": "closed",  # Mark conversation as closed
                    "assigned_agent": None  # Unassign the agent
                })
                conversation_ref.delete()  # Delete the conversation document
                return json.dumps({'message': 'Conversation successfully closed and agent unassigned.'}), 200, headers
            elif status == "no":
                print(f"Conversation remains open for process_code: {process_code}")  # Debugging statement
                return json.dumps({'message': 'Conversation remains open.'}), 200, headers

        # If the role is neither agent nor user, return an error
        print("Error: Invalid role")  # Debugging statement
        return json.dumps({'error': 'Invalid role. Expected "agent" or "user".'}), 400, headers

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)  # Debugging: log the error
        return json.dumps({'error': error_message}), 500, headers
