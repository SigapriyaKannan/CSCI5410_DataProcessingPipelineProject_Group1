from google.cloud import firestore
import json

db = firestore.Client()

def agent_reply(request):
    try:
        if request.method == 'OPTIONS':
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
            print(f"Preflight CORS headers: {headers}")
            return ('', 204, headers)

        headers = {
            "Access-Control-Allow-Origin": "*"
        }
        print(f"Response CORS headers: {headers}")

        request_json = request.get_json()
        if not request_json:
            print("Error: Missing request body")
            return json.dumps({"error": "Invalid request, missing JSON body"}), 400, headers

        agent_email = request_json.get('agent_email')
        process_code = request_json.get('process_code')
        message = request_json.get('message')

        print(f"Received data - agent_email: {agent_email}, process_code: {process_code}, message: {message}")

        if not all([agent_email, process_code, message]):
            print("Error: Missing required fields")
            return json.dumps({"error": "Missing required fields"}), 400, headers

        conversation_ref = db.collection('conversations').document(process_code)
        conversation_doc = conversation_ref.get()

        if not conversation_doc.exists:
            print(f"Error: Conversation not found for process_code: {process_code}")
            return json.dumps({"error": "Conversation not found for the provided process_code"}), 404, headers

        conversation_data = conversation_doc.to_dict()
        if conversation_data.get("assigned_agent") != agent_email:
            print(f"Error: Agent {agent_email} not assigned to this conversation")
            return json.dumps({"error": "Agent is not assigned to this conversation"}), 403, headers

        conversation_ref.update({
            "messages": firestore.ArrayUnion([{
                "sender": "agent",
                "agent_email": agent_email,
                "message": message
            }])
        })

        updated_conversation_doc = conversation_ref.get()
        updated_conversation_data = updated_conversation_doc.to_dict()
        messages = updated_conversation_data.get("messages", [])

        print(f"Agent reply added successfully for process_code: {process_code}")

        return json.dumps({
            "message": "Agent reply successfully added"
        }), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")
        return json.dumps({"error": str(e)}), 500, headers
