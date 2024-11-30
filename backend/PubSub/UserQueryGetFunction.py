import json
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()

# Firestore collection name
COLLECTION_NAME = 'pubsub_data'

def store_data(request):
    """HTTP Cloud Function to store data in Firestore with user_email as document ID and process codes as a map."""
    try:
        # Parse the incoming JSON payload
        data = request.get_json()
        print("Parsed JSON data:", data)

        if not data:
            return json.dumps({'error': 'No data provided'}), 400

        # Extract the user email, role, and records
        user_email = data.get('user_email')
        role = data.get('role')
        records = data.get('data', [])

        if not user_email or not role or not records:
            return json.dumps({'error': 'Missing required fields in payload'}), 400

        # Prepare the process codes data as a map
        process_map = {}
        for record in records:
            process_code = record.get('process_code')
            if not process_code:
                return json.dumps({'error': 'Each record must contain a process_code'}), 400

            # Store process code data as a map
            process_map[process_code] = {
                'job_status': record.get('JobStatus'),
                'processed_file_name': record.get('processed_file_name'),
                'row_count': record.get('RowCount'),
                's3_csv_file_path': record.get('S3CsvFilePath'),
                's3_json_file_path': record.get('S3JsonFilePath'),
                'schema_types': record.get('SchemaTypes'),
                'timestamp': record.get('Timestamp'),
                'filename': record.get('filename'),
                'file_size': record.get('file_size'),
                'Url': record.get('Url')
            }

        # Firestore document reference
        doc_ref = db.collection(COLLECTION_NAME).document(user_email)

        # Merge the data into the document
        doc_data = {
            'user_email': user_email,
            'role': role,
            'process_codes': process_map
        }

        # Save to Firestore (merge existing data)
        doc_ref.set(doc_data, merge=True)
        print(f"Data for {user_email} saved successfully.")

        return json.dumps({'message': f'Data for {user_email} processed successfully'}), 200

    except Exception as e:
        print(f"Error processing data: {e}")
        return json.dumps({'error': str(e)}), 500
