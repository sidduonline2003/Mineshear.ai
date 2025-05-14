from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from pydantic import BaseModel

from app.models.notebook import Notebook # For response model hint
from app.models.task import Task # For response model hint
from app.services import notebook_service # Import the service

# Placeholder for authentication dependency
from app.api.v1.deps import get_current_user_placeholder # Using placeholder for now
from app.models.user import User # For type hinting current_user

router = APIRouter()

class NotebookGenerateRequest(BaseModel):
    topic: str

class NotebookGenerateResponse(BaseModel):
    task_id: str
    notebook_id: str
    # Optionally, include initial status or other details
    notebook_initial_status: str
    task_initial_status: str

@router.post("/generate", 
             response_model=NotebookGenerateResponse, 
             status_code=status.HTTP_202_ACCEPTED)
async def generate_notebook_request(
    request_data: NotebookGenerateRequest,
    background_tasks: BackgroundTasks,
    # Use the placeholder dependency for now. Replace with actual Firebase auth dep later.
    current_user: User = Depends(get_current_user_placeholder) 
):
    """
    Accepts a topic, creates a task and a notebook document,
    and triggers a background task for notebook generation.
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
    print(f"User {user_id} requested to generate notebook for topic: {request_data.topic}")

    try:
        created_notebook, created_task = await notebook_service.create_notebook_and_task(
            topic=request_data.topic, 
            user_id=user_id,
            background_tasks=background_tasks
        )
    except Exception as e:
        # Handle exceptions from the service layer, e.g., Firestore connection issues
        print(f"Error calling notebook_service.create_notebook_and_task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate notebook generation: {str(e)}"
        )
    
    print(f"Notebook creation initiated. Notebook ID: {created_notebook.notebook_id}, Task ID: {created_task.task_id}")

    return NotebookGenerateResponse(
        notebook_id=created_notebook.notebook_id,
        task_id=created_task.task_id,
        notebook_initial_status=created_notebook.status.value,
        task_initial_status=created_task.status.value
    )

# GET /api/v1/notebooks/{notebook_id} - To fetch notebook status/content
@router.get("/{notebook_id}", response_model=Notebook)
async def get_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user_placeholder)
):
    if not current_user or not current_user.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    notebook = await notebook_service.get_notebook_by_id(notebook_id=notebook_id, user_id=current_user.user_id)
    if not notebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found or access denied")
    return notebook
