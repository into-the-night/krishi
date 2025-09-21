import firebase_admin
from firebase_admin import credentials, messaging

from config.settings import settings

cred = credentials.Certificate(settings.firebase_credentials_path)
firebase_admin.initialize_app(cred)

def subscribe_to_topic(topic: str, tokens: list[str]):
    try:
        response = messaging.subscribe_to_topic(tokens, topic)
        print(f"Successfully subscribed to topic: {response.success_count} succeeded, {response.failure_count} failed")
    except Exception as e:
        print(f"Error subscribing to topic: {e}")