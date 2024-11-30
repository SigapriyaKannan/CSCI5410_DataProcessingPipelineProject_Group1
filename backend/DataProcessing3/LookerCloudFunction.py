import os
import json
from google.cloud import firestore, bigquery

# Initialize Firestore client
db = firestore.Client()

# Firestore collection name
COLLECTION_NAME = 'wordcloud_data'


def process_word_cloud_data(request):
    """
    Cloud Function to process word cloud data. Saves data to Firestore and triggers BigQuery insertion.
    """
    try:
        # Log the raw request body
        print("Raw request data:", request.data)

        # Parse JSON data from the request
        data = request.get_json()
        print("Parsed JSON data:", data)

        if not data:
            print("No data provided in request.")
            return json.dumps({'error': 'No data provided'}), 400

        # Extract fields from the request
        user_email = data.get('user_email')
        filename = data.get('filename')
        word_frequency = data.get('word_frequency')  # Expected to be a dictionary of {word: frequency}

        # Log individual fields
        print(f"user_email: {user_email}, filename: {filename}, word_frequency: {word_frequency}")

        # Validate required fields
        if not all([user_email, filename, word_frequency]):
            print("Missing required fields.")
            return json.dumps({'error': 'Missing required fields'}), 400

        # Save to Firestore
        save_to_firestore(user_email, filename, word_frequency)

        # Store data in BigQuery
        bigquery_response = store_data_in_bigquery(user_email, filename, word_frequency)

        if "error" in bigquery_response:
            return json.dumps(bigquery_response), 500

        return json.dumps({'message': f'Data for {filename} processed successfully'}), 200

    except Exception as e:
        print(f"Error processing word cloud data: {e}")
        return json.dumps({'error': str(e)}), 500


def save_to_firestore(user_email, filename, word_frequency):
    """
    Save word cloud data to Firestore under a document with user_email as ID.
    """
    try:
        # Firestore document reference
        doc_ref = db.collection(COLLECTION_NAME).document(user_email)

        # Prepare data to save
        doc_data = {
            'file_name': filename,
            'word_frequency': word_frequency
        }

        # Save data to Firestore
        doc_ref.set(doc_data)
        print(f"Data for {filename} saved successfully to Firestore.")

    except Exception as e:
        print(f"Error saving data to Firestore: {e}")
        raise


def store_data_in_bigquery(user_email, filename, word_frequency):
    """
    Store word cloud data in BigQuery table.
    """
    try:
        # Initialize BigQuery client
        client = bigquery.Client()

        # BigQuery dataset and table
        dataset_id = "WordCloudData"
        table_id = "WordCloudTable"

        # Construct table reference
        table_ref = f"{client.project}.{dataset_id}.{table_id}"

        # Prepare rows for insertion
        rows_to_insert = [
            {"user_email": user_email, "file_name": filename, "word": word, "frequency": frequency}
            for word, frequency in word_frequency.items()
        ]

        # Insert rows into BigQuery
        errors = client.insert_rows_json(table_ref, rows_to_insert)

        if errors:
            print(f"Errors occurred while inserting rows: {errors}")
            return {"error": "Failed to store data in BigQuery", "details": errors}
        else:
            print(f"Data successfully inserted into {table_ref}")
            return {"message": "Data successfully stored in BigQuery"}

    except Exception as e:
        print(f"Error storing data in BigQuery: {e}")
        raise
