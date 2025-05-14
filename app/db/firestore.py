import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import os

# Global variable to hold the Firestore client
db = None

def initialize_firebase_admin():
    global db
    if not firebase_admin._apps:
        # Ensure the path is not None and the file exists
        if settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH and \
           os.path.exists(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH):
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
            db = firestore.client()
        elif settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH:
            print(f"Warning: Firebase service account key file not found at {settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH}. Firestore will not be available.")
        else:
            print("Warning: FIREBASE_SERVICE_ACCOUNT_KEY_PATH is not set. Firestore will not be available.")
    else:
        # Already initialized, ensure db client is available
        if db is None:
            db = firestore.client()
        print("Firebase Admin SDK already initialized.")

def get_firestore_client():
    global db
    if db is None:
        # This might happen if initialization was skipped or failed,
        # and an attempt is made to get the client.
        # Depending on strictness, you could raise an error here.
        print("Warning: Firestore client requested but not initialized. Attempting to initialize now.")
        initialize_firebase_admin() # Try to initialize
        if db is None: # If still None after attempt
             raise Exception("Firestore client is not available. Firebase Admin SDK might not have been initialized correctly.")
    return db

# Example of how you might use this (CRUD operations will go into service layers or specific db interaction files)
# async def get_document(collection_name: str, document_id: str):
#     client = get_firestore_client()
#     doc_ref = client.collection(collection_name).document(document_id)
#     doc = await doc_ref.get() # For async, use firestore.AsyncClient and async methods
#     if doc.exists:
#         return doc.to_dict()
#     return None

# Note: For a production FastAPI app, especially with async endpoints,
# you should use `firebase_admin.firestore.AsyncClient`.
# The current `firestore.client()` is synchronous.
# For this iteration, we'll keep it simple and address async client later if needed.
# Let's assume for now that background tasks might use this sync client,
# and API endpoints needing direct Firestore access would be refactored for async if performance becomes an issue.
