from google.cloud import firestore
import json

db = firestore.Client()


def fetch_chat_messages(request):
    try:
        if request.method == 'OPTIONS':
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
            return ('', 204, headers)

        headers = {
            "Access-Control-Allow-Origin": "*"
        }
        print(f"Response CORS headers: {headers}")

        request_json = request.get_json()
        if not request_json:
            print("Error: Missing request body")
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        process_code = request_json.get('process_code')
        if not process_code:
            print("Error: Missing process_code")
            return json.dumps({'error': 'Missing required field: process_code'}), 400, headers

        print(f"Fetching conversation for process_code: {process_code}")

        conversation_ref = db.collection('conversations').document(process_code)
        conversation_doc = conversation_ref.get()

        if not conversation_doc.exists:
            print(f"Error: Conversation not found for process_code: {process_code}")
            return json.dumps({'error': 'Conversation not found for the provided process_code'}), 404, headers

        conversation_data = conversation_doc.to_dict()
        messages = conversation_data.get('messages', [])

        print(f"Retrieved messages for process_code {process_code}: {messages}")

        return json.dumps({
            'message': 'Chat fetched successfully',
            'messages': messages
        }), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")
        return json.dumps({'error': str(e)}), 500, headers
