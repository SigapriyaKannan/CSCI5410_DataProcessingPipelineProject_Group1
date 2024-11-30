from google.cloud import firestore, pubsub_v1
import json
import random

# Firestore client
db = firestore.Client()

# Pub/Sub client
publisher = pubsub_v1.PublisherClient()

# Pub/Sub topic details
PROJECT_ID = "serverless-440903"
TOPIC_NAME = "serverlessModule3"
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

def publish_message(request):
    """HTTP API to publish a message to Pub/Sub."""
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
            "Access-Control-Allow-Origin": "*"  # Allow all origins (you can replace "*" with your frontend URL for better security)
        }
        print(f"Response CORS headers: {headers}")  # Debugging: check response headers

        # Parse the request JSON
        request_json = request.get_json()
        if not request_json:
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        user_email = request_json.get('user_email')
        process_code = request_json.get('process_code')
        message = request_json.get('message')

        # Validate input
        if not all([user_email, process_code, message]):
            return json.dumps({'error': 'Missing required fields: user_email, process_code, and message'}), 400, headers

        # Fetch pubsub_data document for the given user
        pubsub_ref = db.collection('pubsub_data').document(user_email)
        pubsub_doc = pubsub_ref.get()

        if not pubsub_doc.exists:
            return json.dumps({'error': 'No pubsub data found for the given user_email'}), 404, headers

        # Extract process codes from the document and validate
        pubsub_data = pubsub_doc.to_dict()
        process_codes = pubsub_data.get("process_codes", {})
        if process_code not in process_codes:
            return json.dumps({'error': f"Process code {process_code} not found for the given user_email"}), 404, headers

        # Fetch available agents from `appUser_data`
        agents_ref = db.collection("appUser_data").where("role", "==", "agent").stream()
        agents = [agent.to_dict().get("user_email") for agent in agents_ref if agent.to_dict().get("user_email")]

        if not agents:
            return json.dumps({'error': 'No available agents to assign'}), 500, headers

        # Randomly select an agent
        assigned_agent = random.choice(agents)

        # Log the conversation using `process_code` as the document ID
        conversation_ref = db.collection("conversations").document(process_code)
        conversation_ref.set({
            "user_email": user_email,
            "assigned_agent": assigned_agent,
            "messages": firestore.ArrayUnion([{
                "sender": "user",
                "message": message
            }])
        }, merge=True)

        # Publish the message to Pub/Sub
        pubsub_message = {
            "user_email": user_email,
            "process_code": process_code,
            "message": message
        }
        future = publisher.publish(topic_path, json.dumps(pubsub_message).encode("utf-8"))
        future.result()  # Wait for the message to be published

        # Success response
        return json.dumps({
            "message": "Message published successfully",
            "assigned_agent": assigned_agent
        }), 200, headers

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)  # Debugging: log the error
        return json.dumps({'error': error_message}), 500, headers
