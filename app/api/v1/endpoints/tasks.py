from fastapi import APIRouter, HTTPException, status, Depends

from app.models.task import Task # Response model
from app.services import task_service # Import the new service

# Placeholder for authentication dependency
from app.api.v1.deps import get_current_user_placeholder
from app.models.user import User # For type hinting current_user

router = APIRouter()

@router.get("/{task_id}", response_model=Task)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user_placeholder) # Use placeholder auth
):
    """
    Get the status and details of a specific task.
    """
    if not current_user or not current_user.user_id:
        # This check is more for verbosity with the placeholder.
        # A real auth dependency would raise HTTPException if user is not authenticated.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or user_id is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = current_user.user_id
    task = await task_service.get_task_by_id(task_id=task_id, user_id=user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID {task_id} not found or access denied."
        )
    
    return task
