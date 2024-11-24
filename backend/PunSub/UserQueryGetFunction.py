import json
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()

# Firestore collection name
COLLECTION_NAME = 'pubsub_data'

def store_data(request):
    """HTTP Cloud Function to store data in Firestore without validation."""
    try:
        # Parse the incoming JSON payload
        data = request.get_json()
        print("Parsed JSON data:", data)

        if not data:
            return json.dumps({'error': 'No data provided'}), 400

        # Extract the user email and records
        user_email = data.get('user_email')
        role = data.get('role')
        records = data.get('data', [])

        if not user_email or not role or not records:
            return json.dumps({'error': 'Missing required fields in payload'}), 400

        # Process and save each record to Firestore
        for record in records:
            process_code = record.get('process_code')
            job_status = record.get('JobStatus')
            processed_file_name = record.get('processed_file_name')
            row_count = record.get('RowCount')
            s3_csv_file_path = record.get('S3CsvFilePath')
            s3_json_file_path = record.get('S3JsonFilePath')
            schema_types = record.get('SchemaTypes')
            timestamp = record.get('Timestamp')

            # Firestore document ID: Combine email and process_code for uniqueness
            doc_id = f"{user_email}_{process_code}"
            doc_ref = db.collection(COLLECTION_NAME).document(doc_id)

            # Document data (no validation, just copy all fields)
            doc_data = {
                'user_email': user_email,
                'role': role,
                'process_code': process_code,
                'job_status': job_status,
                'processed_file_name': processed_file_name,
                'row_count': row_count,
                's3_csv_file_path': s3_csv_file_path,
                's3_json_file_path': s3_json_file_path,
                'schema_types': schema_types,
                'timestamp': timestamp
            }

            # Save to Firestore
            doc_ref.set(doc_data)
            print(f"Record with process_code {process_code} saved for user {user_email}.")

        return json.dumps({'message': f'All records for {user_email} processed successfully'}), 200

    except Exception as e:
        print(f"Error processing data: {e}")
        return json.dumps({'error': str(e)}), 500
