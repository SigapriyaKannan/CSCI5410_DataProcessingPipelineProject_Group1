import os
import json
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()

# Firestore collection name
COLLECTION_NAME = 'wordcloud_data'

def process_word_cloud_data(request):
    # Log the raw request body to see what is being received
    print("Raw request data:", request.data)

    # Attempt to parse JSON data from the request
    data = request.get_json()

    # Log the parsed data to verify its structure
    print("Parsed JSON data:", data)

    if not data:
        print("No data provided in request.")
        return json.dumps({'error': 'No data provided'}), 400

    user_email = data.get('user_email')
    role = data.get('role')
    filename = data.get('filename')
    word_frequency = data.get('word_frequency')

    # Log individual fields to ensure they're correctly parsed
    print(f"user_email: {user_email}, role: {role}, filename: {filename}, word_frequency: {word_frequency}")

    if not all([user_email, role, filename, word_frequency]):
        print("Missing required fields.")
        return json.dumps({'error': 'Missing required fields'}), 400

    # Write to Firestore
    try:
        # Firestore document id can be the filename
        doc_ref = db.collection(COLLECTION_NAME).document(filename)

        # Create document data
        doc_data = {
            'user_email': user_email,
            'role': role,
            'filename': filename,
            'word_frequency': word_frequency
        }

        # Save the data to Firestore
        doc_ref.set(doc_data)

        print(f"Data for {filename} saved successfully to Firestore.")
        return json.dumps({'message': f'Word cloud data for {filename} saved successfully'}), 200

    except Exception as e:
        print(f"Error saving data to Firestore: {e}")
        return json.dumps({'error': str(e)}), 500
