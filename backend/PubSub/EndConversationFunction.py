from google.cloud import firestore
import json

# Firestore client
db = firestore.Client()


def end_conversation(request):
    """Endpoint to end a conversation based on user or agent request."""
    try:
        # Parse incoming JSON request
        request_json = request.get_json()
        if not request_json:
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400

        agent_email = request_json.get('agent_email')  # Agent's email (if agent is triggering)
        user_email = request_json.get('user_email')  # User's email (for user-triggered requests)
        role = request_json.get('role')  # Role of the user or agent (agent/user)
        status = request_json.get('status')  # "resolved" or "closed" (for agent)

        # Validate input fields
        if not all([role, agent_email or user_email]):
            return json.dumps({'error': 'Missing required fields: role and either agent_email or user_email'}), 400

        # If triggered by the agent
        if role == "agent" and agent_email:
            if not status or status not in ['yes', 'no']:
                return json.dumps({'error': 'If role is agent, "status" is required with value "yes" or "no".'}), 400

            # Fetch the active conversation where the agent is assigned
            conversation_ref = db.collection('conversations').where('assigned_agent', '==', agent_email).limit(
                1).stream()
            conversation = None
            for conv in conversation_ref:
                conversation = conv.to_dict()
                conversation_document_ref = conv.reference  # Get the document reference
                break

            if not conversation:
                return json.dumps({'error': 'No active conversation found for the provided agent_email'}), 404

            # Fetch the user email from the conversation
            user_email = conversation['user_email']

            # Mark as resolved and unassign agent if status is 'yes'
            if status == 'yes':
                conversation_document_ref.update({
                    "status": "resolved",  # Mark conversation as resolved
                    "assigned_agent": None,  # Unassign the agent
                })
                return json.dumps({'message': 'Conversation marked as resolved and agent unassigned.'}), 200

            elif status == 'no':
                return json.dumps({'message': 'Conversation is not yet resolved. Agent remains assigned.'}), 200

        # If triggered by the user
        if role == "user" and user_email:
            # Fetch the conversation for the user
            conversation_ref = db.collection('conversations').document(user_email)
            conversation_doc = conversation_ref.get()

            if not conversation_doc.exists:
                return json.dumps({'error': 'Conversation not found for the provided user_email'}), 404

            conversation_data = conversation_doc.to_dict()

            # Mark as closed and unassign the agent
            conversation_ref.update({
                "status": "closed",  # Mark conversation as closed
                "assigned_agent": None,  # Unassign the agent
            })

            return json.dumps({'message': 'Conversation successfully ended and agent unassigned.'}), 200

        # If the role is neither agent nor user, return an error
        return json.dumps({'error': 'Invalid role. Expected "agent" or "user".'}), 400

    except Exception as e:
        return json.dumps({'error': str(e)}), 500
