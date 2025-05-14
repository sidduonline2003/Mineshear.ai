from fastapi import HTTPException, status
from app.models.user import User # Assuming User model has user_id

# --- Placeholder Authentication Dependency ---
# This is a temporary placeholder. In a real application, this would involve:
# - Extracting a Firebase ID token from the request Authorization header.
# - Verifying the token using firebase_admin.auth.verify_id_token().
# - Optionally, fetching user details from Firestore based on the decoded token's UID.

async def get_current_user_placeholder() -> User:
    """
    Placeholder for Firebase ID token verification.
    Returns a dummy User object for development purposes.
    In a real app, this would verify a token and fetch/construct a real User model.
    """
    print("DEBUG: Using placeholder authentication. Returning dummy user.")
    # Replace with actual user retrieval logic when Firebase Auth is implemented.
    # For now, we simulate an authenticated user.
    # This dummy user_id should ideally be consistent if you want to test ownership,
    # or you can make it dynamic if your Firestore rules are open for initial testing.
    return User(
        user_id="dev_user_123", # Dummy Firebase UID
        email="dev.user@example.com", 
        display_name="Dev User",
        photo_url=None,
        created_at="2023-01-01T12:00:00Z" # Needs to be a valid ISO 8601 datetime string or datetime object
    )

# --- Actual Firebase Auth Dependency (to be implemented later) ---
# from fastapi import Depends, Security
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import firebase_admin
# from firebase_admin import auth
# from app.core.config import settings # If needed for specific settings
# from app.db.firestore import get_firestore_client # If you fetch user from DB

# oauth2_scheme = HTTPBearer()

# async def get_current_user(token: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> User:
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authenticated - No token provided",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     id_token = token.credentials
#     try:
#         decoded_token = auth.verify_id_token(id_token)
#         uid = decoded_token['uid']
        
        # Option 1: Return a User model based only on token data
        # return User(
        #     user_id=uid,
        #     email=decoded_token.get('email'),
        #     display_name=decoded_token.get('name'),
        #     # photo_url=decoded_token.get('picture') # if available in token
        #     # created_at will not be available from token, needs db fetch or omit for this model instance
        # )

        # Option 2: Fetch full user profile from Firestore (preferred for more details)
#         db = get_firestore_client()
#         user_ref = db.collection("users").document(uid)
#         user_doc = user_ref.get()
#         if user_doc.exists:
#             user_data = user_doc.to_dict()
#             # Ensure created_at is a datetime object if fetched from Firestore as a Timestamp
#             # Pydantic should handle the conversion if the type hint is datetime
#             return User(user_id=uid, **user_data)
#         else:
            # This case means a user exists in Firebase Auth but not in your Firestore user collection.
            # You might want to create it here, or raise an error.
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, 
#                 detail=f"User with ID {uid} not found in Firestore."
#             )

#     except firebase_admin.auth.RevokedIdTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token revoked, user is signed out",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except firebase_admin.auth.UserDisabledError:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="User account has been disabled",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except (firebase_admin.auth.InvalidIdTokenError, Exception) as e:
#         print(f"Token verification failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Could not validate credentials: Invalid token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
