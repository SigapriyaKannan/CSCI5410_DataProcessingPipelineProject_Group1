from google.cloud import firestore
import json

db = firestore.Client()


def get_process_codes(request):

    try:

        if request.method == 'OPTIONS':
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
            }
            print(f"Preflight CORS headers: {headers}")
            return ('', 204, headers)

        headers = {
            "Access-Control-Allow-Origin": "*"
        }

        request_json = request.get_json()
        if not request_json:
            return json.dumps({'error': 'Invalid request, missing JSON body'}), 400, headers

        user_email = request_json.get('user_email')
        if not user_email:
            return json.dumps({'error': 'Missing required field: user_email'}), 400, headers

        pubsub_ref = db.collection('pubsub_data').document(user_email)
        pubsub_doc = pubsub_ref.get()

        if not pubsub_doc.exists:
            return json.dumps({'error': 'No process codes found for the given user_email'}), 404, headers

        pubsub_data = pubsub_doc.to_dict()
        process_codes = list(pubsub_data.get('process_codes', {}).keys())

        print(f"Found process codes for {user_email}: {process_codes}")  # Debugging: check process codes

        return json.dumps({'codes': process_codes}), 200, headers

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)
        return json.dumps({'error': error_message}), 500, headers
