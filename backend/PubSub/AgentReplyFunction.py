from google.cloud import firestore
import json

# Firestore client
db = firestore.Client()

def agent_reply(request):
    """Endpoint for agent to reply to a conversation."""
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
            "Access-Control-Allow-Origin": "*"  # Allow all origins (replace "*" with your frontend URL for better security)
        }
        print(f"Response CORS headers: {headers}")  # Debugging: check response headers

        # Parse request JSON
        request_json = request.get_json()
        if not request_json:
            print("Error: Missing request body")  # Debugging statement
            return json.dumps({"error": "Invalid request, missing JSON body"}), 400, headers

        agent_email = request_json.get('agent_email')
        process_code = request_json.get('process_code')  # Include process_code to identify the conversation
        message = request_json.get('message')

        print(f"Received data - agent_email: {agent_email}, process_code: {process_code}, message: {message}")  # Debugging statement

        # Ensure all required fields are provided
        if not all([agent_email, process_code, message]):
            print("Error: Missing required fields")  # Debugging statement
            return json.dumps({"error": "Missing required fields"}), 400, headers

        # Fetch the conversation by process_code
        conversation_ref = db.collection('conversations').document(process_code)
        conversation_doc = conversation_ref.get()

        if not conversation_doc.exists:
            print(f"Error: Conversation not found for process_code: {process_code}")  # Debugging statement
            return json.dumps({"error": "Conversation not found for the provided process_code"}), 404, headers

        # Ensure the agent is assigned to the conversation
        conversation_data = conversation_doc.to_dict()
        if conversation_data.get("assigned_agent") != agent_email:
            print(f"Error: Agent {agent_email} not assigned to this conversation")  # Debugging statement
            return json.dumps({"error": "Agent is not assigned to this conversation"}), 403, headers

        # Update the conversation with the agent's reply
        conversation_ref.update({
            "messages": firestore.ArrayUnion([{
                "sender": "agent",
                "agent_email": agent_email,
                "message": message
            }])
        })

        # Fetch updated messages
        updated_conversation_doc = conversation_ref.get()
        updated_conversation_data = updated_conversation_doc.to_dict()
        messages = updated_conversation_data.get("messages", [])

        print(f"Agent reply added successfully for process_code: {process_code}")  # Debugging statement

        return json.dumps({
            "message": "Agent reply successfully added"
        }), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging statement
        return json.dumps({"error": str(e)}), 500, headers
