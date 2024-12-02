from google.cloud import firestore
import json

db = firestore.Client()

def get_agent_conversations(request):
    try:

        if request.method == 'OPTIONS':
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
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
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        agent_email = request_json.get('agent_email')
        if not agent_email:
            print("Error: Missing agent_email field")
            return json.dumps({'error': 'Missing required field: agent_email'}), 400, headers

        print(f"Fetching conversations assigned to agent: {agent_email}")

        conversations_ref = db.collection('conversations').where('assigned_agent', '==', agent_email).stream()

        process_codes = [doc.id for doc in conversations_ref]

        if not process_codes:
            print(f"No assigned conversations found for agent: {agent_email}")
            return json.dumps({'message': 'No assigned conversations found for the agent'}), 404, headers

        print(f"Found conversations for agent {agent_email}: {process_codes}")

        return json.dumps({'conversations': process_codes}), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")
        return json.dumps({'error': str(e)}), 500, headers
