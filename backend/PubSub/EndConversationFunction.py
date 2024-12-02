from google.cloud import firestore
import json

db = firestore.Client()

def end_conversation(request):
    try:
        print(f"Received request: {request}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {request.headers}")

        if request.method == 'OPTIONS':
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
            print(f"Preflight CORS headers: {headers}")
            return ('', 204, headers)

        headers = {
            "Access-Control-Allow-Origin": "*",
        }
        print(f"Response CORS headers: {headers}")

        request_json = request.get_json()
        if not request_json:
            print("Error: Missing JSON body")
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        process_code = request_json.get('process_code')
        role = request_json.get('role')
        status = request_json.get('status')

        print(f"Parsed data - process_code: {process_code}, role: {role}, status: {status}")

        if not all([process_code, role, status]):
            print("Error: Missing required fields")
            return json.dumps({'error': 'Missing required fields: process_code, role, and status'}), 400, headers

        if status not in ["yes", "no"]:
            print("Error: Invalid status value")
            return json.dumps({'error': 'Invalid status value. It should be "yes" or "no".'}), 400, headers

        conversation_ref = db.collection('conversations').document(process_code)
        conversation_doc = conversation_ref.get()

        if not conversation_doc.exists:
            print(f"Error: Conversation not found for process_code: {process_code}")  # Debugging statement
            return json.dumps({'error': 'Conversation not found for the provided process_code'}), 404, headers


        if role == "agent":
            if status == "yes":
                print(f"Marking conversation as resolved and deleting for process_code: {process_code}")
                conversation_ref.update({
                    "assigned_agent": None,
                    "status": "resolved"
                })
                conversation_ref.delete()
                return json.dumps({'message': 'Conversation resolved, agent unassigned, and conversation deleted.'}), 200, headers
            elif status == "no":
                print(f"Conversation not resolved. Agent remains assigned for process_code: {process_code}")
                return json.dumps({'message': 'Conversation not resolved. Agent remains assigned.'}), 200, headers

        elif role == "user":
            if status == "yes":
                print(f"Closing conversation and deleting for process_code: {process_code}")
                conversation_ref.update({
                    "status": "closed",
                    "assigned_agent": None
                })
                conversation_ref.delete()
                return json.dumps({'message': 'Conversation successfully closed and agent unassigned.'}), 200, headers
            elif status == "no":
                print(f"Conversation remains open for process_code: {process_code}")
                return json.dumps({'message': 'Conversation remains open.'}), 200, headers

        print("Error: Invalid role")
        return json.dumps({'error': 'Invalid role. Expected "agent" or "user".'}), 400, headers

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)
        return json.dumps({'error': error_message}), 500, headers
