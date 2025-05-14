from typing import Optional
from app.db.firestore import get_firestore_client
from app.models.task import Task

async def get_task_by_id(task_id: str, user_id: str) -> Optional[Task]:
    """
    Retrieves a specific task by its ID from Firestore.
    Ensures that the task belongs to the requesting user for basic access control.
    """
    db = get_firestore_client()
    task_ref = db.collection("tasks").document(task_id)
    doc = task_ref.get()

    if doc.exists:
        task_data = doc.to_dict()
        # Basic authorization: Check if the task belongs to the user_id making the request
        if task_data.get("user_id") == user_id:
            return Task(**task_data, task_id=doc.id) # task_id=doc.id ensures it's part of the model
        else:
            # Task exists, but does not belong to the user. Treat as not found for security.
            print(f"User {user_id} attempted to access task {task_id} owned by {task_data.get('user_id')}")
            return None 
    return None
