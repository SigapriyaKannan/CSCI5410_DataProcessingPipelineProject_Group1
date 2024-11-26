from google.cloud import firestore
import json

# Firestore client
db = firestore.Client()

def agent_reply(request):
    """Endpoint for agent to reply to a conversation."""
    try:
        # Parse incoming JSON request
        request_json = request.get_json()
        if not request_json:
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400

        agent_email = request_json.get('agent_email')
        message = request_json.get('message')

        # Validate input fields
        if not all([agent_email, message]):
            return json.dumps({'error': 'Missing required fields'}), 400

        # Find the active conversation where the agent is assigned
        print(f"Fetching active conversation for agent: {agent_email}")
        conversation_ref = db.collection('conversations').where('assigned_agent', '==', agent_email).limit(1).stream()

        # If there’s no active conversation for this agent, return an error
        conversation = None
        for conv in conversation_ref:
            conversation = conv.to_dict()
            break

        if not conversation:
            return json.dumps({'error': 'No active conversation found for the agent'}), 404

        # The user email is fetched from the conversation data
        user_email = conversation['user_email']

        # Append the agent's reply to the conversation's messages (without timestamp)
        conversation_ref = db.collection("conversations").document(user_email)
        conversation_ref.update({
            "messages": firestore.ArrayUnion([{
                "sender": "agent",
                "agent_email": agent_email,
                "message": message
            }])
        })

        return json.dumps({'message': 'Agent reply successfully added'}), 200

    except Exception as e:
        return json.dumps({'error': str(e)}), 500
