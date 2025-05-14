from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    # Firebase UID will be the document ID in Firestore users/{userId}
    # We don't store it as a field within the document itself typically if it's the ID.
    # However, if you had a separate auto-generated user_id and wanted to store firebase_uid as a field, you could.

class UserCreate(UserBase):
    # This model might be used if you have a separate user creation endpoint,
    # but often users are created via Firebase Auth and then a corresponding Firestore doc is made.
    user_id: str # This would be the Firebase UID
    display_name: Optional[str] = None
    photo_url: Optional[str] = None # From Firebase Auth
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserInDB(UserBase):
    # Assuming user_id (Firebase UID) is the document ID, it won't be a field in the document itself.
    # If you decide to store it explicitly, add it here.
    # user_id: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    # last_login_at: Optional[datetime] = None # Could be useful
    # custom_claims: Optional[Dict[str, Any]] = None # For role-based access if synced from Firebase

    class Config:
        from_attributes = True

class User(UserInDB):
    """
    Represents a User document as stored in Firestore and potentially returned to the client.
    The user_id (Firebase UID) is typically the ID of the Firestore document (e.g., users/{userId}).
    """
    # If you want to explicitly include the user_id (Firebase UID) in the response model:
    user_id: str # The Firebase UID, which is the doc ID.
    pass

# Note on User Model Design with Firestore:
# Typically, for a `users/{userId}` collection in Firestore, the `userId` (which is the Firebase UID)
# is the ID of the document. So, the `userId` field itself might not be stored *inside* the document's data.
# When you retrieve a user document, you already know its ID. 
# The `User` model above includes `user_id` for convenience in API responses or internal use 
# after fetching the document and its ID.
