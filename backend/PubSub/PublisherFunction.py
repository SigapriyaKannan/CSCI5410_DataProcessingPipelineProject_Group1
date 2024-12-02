from google.cloud import firestore, pubsub_v1
import json
import random

db = firestore.Client()

publisher = pubsub_v1.PublisherClient()

PROJECT_ID = "serverless-440903"
TOPIC_NAME = "serverlessModule3"
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

def publish_message(request):
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
            return ('', 204, headers)

        headers = {
            "Access-Control-Allow-Origin": "*"
        }
        print(f"Response CORS headers: {headers}")

        request_json = request.get_json()
        if not request_json:
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        user_email = request_json.get('user_email')
        process_code = request_json.get('process_code')
        message = request_json.get('message')

        if not all([user_email, process_code, message]):
            return json.dumps({'error': 'Missing required fields: user_email, process_code, and message'}), 400, headers

        pubsub_ref = db.collection('pubsub_data').document(user_email)
        pubsub_doc = pubsub_ref.get()

        if not pubsub_doc.exists:
            return json.dumps({'error': 'No pubsub data found for the given user_email'}), 404, headers

        pubsub_data = pubsub_doc.to_dict()
        process_codes = pubsub_data.get("process_codes", {})
        if process_code not in process_codes:
            return json.dumps({'error': f"Process code {process_code} not found for the given user_email"}), 404, headers

        agents_ref = db.collection("appUser_data").where("role", "==", "agent").stream()
        agents = [agent.to_dict().get("user_email") for agent in agents_ref if agent.to_dict().get("user_email")]

        if not agents:
            return json.dumps({'error': 'No available agents to assign'}), 500, headers

        assigned_agent = random.choice(agents)

        conversation_ref = db.collection("conversations").document(process_code)
        conversation_ref.set({
            "user_email": user_email,
            "assigned_agent": assigned_agent,
            "messages": firestore.ArrayUnion([{
                "sender": "user",
                "message": message
            }])
        }, merge=True)

        pubsub_message = {
            "user_email": user_email,
            "process_code": process_code,
            "message": message
        }
        future = publisher.publish(topic_path, json.dumps(pubsub_message).encode("utf-8"))
        future.result()
        return json.dumps({
            "message": "Message published successfully",
            "assigned_agent": assigned_agent
        }), 200, headers

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        return json.dumps({'error': error_message}), 500, headers
