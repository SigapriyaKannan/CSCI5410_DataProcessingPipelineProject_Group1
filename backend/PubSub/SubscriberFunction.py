from google.cloud import firestore
import base64
import json

db = firestore.Client()

def assign_agent_and_log(request):
    try:
        envelope = request.get_json(silent=True)
        if not envelope or "message" not in envelope:
            return json.dumps({"error": "Invalid Pub/Sub message format"}), 400

        pubsub_message = envelope["message"]
        if "data" not in pubsub_message:
            return json.dumps({"error": "Pub/Sub message missing 'data' field"}), 400

        message_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        data = json.loads(message_data)

        user_email = data.get("user_email")
        process_code = data.get("process_code")
        message = data.get("message")

        if not all([user_email, process_code, message]):
            return json.dumps({"error": "Missing required fields"}), 400

        conversation_ref = db.collection("conversations").document(process_code)
        conversation_ref.update({
            "messages": firestore.ArrayUnion([{
                "sender": "user",
                "message": message
            }])
        })

        conversation_doc = conversation_ref.get()
        if conversation_doc.exists:
            conversation_data = conversation_doc.to_dict()
            messages = conversation_data.get("messages", [])
        else:
            messages = []

        return json.dumps({"message": "Message logged successfully", "messages": messages}), 200

    except Exception as e:
        return json.dumps({"error": str(e)}), 500
