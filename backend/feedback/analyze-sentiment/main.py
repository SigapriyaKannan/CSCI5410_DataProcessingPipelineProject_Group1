import functions_framework
from google.cloud import storage
from google.cloud import firestore
from google.cloud import language_v1
import json

@functions_framework.cloud_event
def analyze_sentiment(cloud_event):
    # Get the file details from the cloud event
    data = cloud_event.data
    bucket_name = data['bucket']
    filename = data['name']

    # Initialize clients
    storage_client = storage.Client()
    firestore_client = firestore.Client()
    language_client = language_v1.LanguageServiceClient()

    try:
        # Retrieve the feedback file from Cloud Storage
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        feedback_data = json.loads(blob.download_as_text())
        feedback_text = feedback_data['feedback']
        feature = feedback_data['feature']

        # Analyze sentiment
        document = language_v1.Document(
            content=feedback_text, 
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        sentiment = language_client.analyze_sentiment(request={'document': document})
        
        # Store sentiment in Firestore
        sentiment_data = {
            'feedback': feedback_text,
            'feature': feature,
            'timestamp': feedback_data['timestamp'],
            'sentiment_score': sentiment.document_sentiment.score,
            'sentiment_magnitude': sentiment.document_sentiment.magnitude
        }
        
        # Add to Firestore collection
        firestore_client.collection('feedback-sentiments').add(sentiment_data)

        return 'Sentiment analysis completed', 200

    except Exception as e:
        print(f'Error in sentiment analysis: {str(e)}')
        return f'Error: {str(e)}', 500
