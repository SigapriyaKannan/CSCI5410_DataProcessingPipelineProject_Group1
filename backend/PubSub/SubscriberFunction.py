from google.cloud import firestore
import base64
import json

# Firestore client
db = firestore.Client()

def assign_agent_and_log(request):
    """Triggered by Pub/Sub push delivery."""
    try:
        envelope = request.get_json(silent=True)
        if not envelope or "message" not in envelope:
            return json.dumps({"error": "Invalid Pub/Sub message format"}), 400

        # Extract Pub/Sub message data
        pubsub_message = envelope["message"]
        if "data" not in pubsub_message:
            return json.dumps({"error": "Pub/Sub message missing 'data' field"}), 400

        # Decode the message data from base64 and load the JSON
        message_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        data = json.loads(message_data)

        # Extract relevant fields from the message
        user_email = data.get("user_email")
        process_code = data.get("process_code")
        message = data.get("message")

        # Validate the required fields
        if not all([user_email, process_code, message]):
            return json.dumps({"error": "Missing required fields"}), 400

        # Append the message to the conversation in Firestore using process_code as the document ID
        conversation_ref = db.collection("conversations").document(process_code)
        conversation_ref.update({
            "messages": firestore.ArrayUnion([{
                "sender": "user",  # You could also add "agent" for agent's reply
                "message": message
            }])
        })

        # Fetch the updated conversation to include all messages
        conversation_doc = conversation_ref.get()
        if conversation_doc.exists:
            conversation_data = conversation_doc.to_dict()
            messages = conversation_data.get("messages", [])
        else:
            messages = []

        # Return the updated conversation
        return json.dumps({"message": "Message logged successfully", "messages": messages}), 200

    except Exception as e:
        return json.dumps({"error": str(e)}), 500
