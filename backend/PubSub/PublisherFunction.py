from google.cloud import firestore, pubsub_v1
import json

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
        # Parse input JSON
        data = request.get_json()
        user_email = data.get('user_email')
        process_code = data.get('process_code')
        message = data.get('message')

        # Validate input
        if not all([user_email, process_code, message]):
            error_message = "Missing required fields: user_email, process_code, and message."
            print(error_message)
            return json.dumps({"error": error_message}), 400

        # Validate process code in `pubsub_data`
        pubsub_ref = db.collection('pubsub_data').document(user_email)
        pubsub_doc = pubsub_ref.get()

        if not pubsub_doc.exists:
            error_message = f"No pubsub data found for email: {user_email}"
            print(error_message)
            return json.dumps({"error": error_message}), 404

        process_codes = pubsub_doc.to_dict().get("process_codes", {})
        if process_code not in process_codes:
            error_message = f"Process code {process_code} not found for email: {user_email}"
            print(error_message)
            return json.dumps({"error": error_message}), 404

        # Publish to Pub/Sub
        pubsub_message = {
            "user_email": user_email,
            "process_code": process_code,
            "message": message
        }
        future = publisher.publish(topic_path, json.dumps(pubsub_message).encode("utf-8"))
        print(f"Published message ID: {future.result()}")
        return json.dumps({"message": "Message published successfully"}), 200

    except Exception as e:
        error_message = f"Error publishing message: {str(e)}"
        print(error_message)
        return json.dumps({"error": error_message}), 500
