from google.cloud import firestore
import base64
import json
import random

# Firestore client
db = firestore.Client()

def assign_agent_and_log(request):
    """Triggered by Pub/Sub push delivery."""
    try:
        # Decode and parse the Pub/Sub message
        envelope = request.get_json(silent=True)
        if not envelope or "message" not in envelope:
            error_message = "Invalid Pub/Sub message format"
            print(error_message)
            return json.dumps({"error": error_message}), 400

        # Extract the Pub/Sub message data
        pubsub_message = envelope["message"]
        if "data" not in pubsub_message:
            error_message = "Pub/Sub message missing 'data' field"
            print(error_message)
            return json.dumps({"error": error_message}), 400

        message_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        data = json.loads(message_data)
        print(f"Received message: {data}")

        # Extract details from the message
        user_email = data.get("user_email")
        process_code = data.get("process_code")
        message = data.get("message")

        # Validate data
        if not all([user_email, process_code, message]):
            error_message = "Missing required fields: user_email, process_code, and message."
            print(error_message)
            return json.dumps({"error": error_message}), 400

        # Validate process code in `pubsub_data`
        print(f"Fetching pubsub data for email: {user_email}")
        pubsub_ref = db.collection("pubsub_data").document(user_email)
        pubsub_doc = pubsub_ref.get()

        if not pubsub_doc.exists:
            error_message = f"No pubsub data found for email: {user_email}"
            print(error_message)
            return json.dumps({"error": error_message}), 404

        print("Pubsub document found.")  # Debug
        pubsub_data = pubsub_doc.to_dict()
        process_codes = pubsub_data.get("process_codes", {})
        if process_code not in process_codes:
            error_message = f"Process code {process_code} not found for email: {user_email}"
            print(error_message)
            return json.dumps({"error": error_message}), 404

        print(f"Process code {process_code} validated.")  # Debug
        process_metadata = process_codes[process_code]

        # Fetch all available agents
        print("Fetching available agents.")  # Debug
        agents_ref = db.collection("appUser_data").where("role", "==", "agent").stream()
        agents = []
        for agent_doc in agents_ref:
            agent_data = agent_doc.to_dict()
            agent_email = agent_data.get("user_email")
            if agent_email:  # Ensure valid email
                agents.append(agent_email)

        if not agents:
            error_message = "No available agents to assign."
            print(error_message)
            return json.dumps({"error": error_message}), 500

        print(f"Available agents: {agents}")  # Debug
        assigned_agent = random.choice(agents)
        print(f"Assigned agent: {assigned_agent}")

        # Log the conversation in Firestore (without timestamp field)
        conversation_ref = db.collection("conversations").document(user_email)
        conversation_ref.set(
            {
                "process_code": process_code,
                "user_email": user_email,
                "assigned_agent": assigned_agent,
                "process_metadata": process_metadata,  # Include process-specific metadata
                "messages": firestore.ArrayUnion(
                    [
                        {
                            "sender": "user",
                            "message": message
                        }
                    ]
                ),
            },
            merge=True,
        )

        success_message = f"Conversation logged successfully for user_email: {user_email}"
        print(success_message)
        return json.dumps({"message": success_message}), 200

    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        print(error_message)
        return json.dumps({"error": error_message}), 500
