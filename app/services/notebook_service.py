from fastapi import BackgroundTasks
from app.db.firestore import get_firestore_client
from app.models.notebook import Notebook, NotebookStatus, NotebookInDBBase
from app.models.task import Task, TaskStatus, ToolType, TaskInDBBase
from app.background.notebook_tasks import generate_notebook_content_task # We'll create this task function soon
from datetime import datetime

async def create_notebook_and_task(
    topic: str, 
    user_id: str, 
    background_tasks: BackgroundTasks
) -> tuple[Notebook, Task]:
    """
    Creates initial Notebook and Task documents in Firestore and 
    schedules the notebook generation as a background task.
    """
    db = get_firestore_client()

    # 1. Create an initial Notebook document
    notebook_data = {
        "topic_input": topic,
        "user_id": user_id,
        "status": NotebookStatus.PENDING,
        # notebook_id, created_at, updated_at will be set by NotebookInDBBase default factories
    }
    # Use NotebookInDBBase to get all default fields populated (like ID, timestamps)
    notebook_to_create = NotebookInDBBase(**notebook_data)
    
    # Save to Firestore
    # Note: Firestore client uses synchronous methods by default.
    # For truly async operations with Firestore, firebase_admin.firestore.AsyncClient should be used.
    # We are keeping it simple for now, assuming this service method might be called in contexts
    # where a brief sync operation is acceptable, or background tasks handle longer work.
    notebook_ref = db.collection("users").document(user_id).collection("notebooks").document(notebook_to_create.notebook_id)
    notebook_ref.set(notebook_to_create.model_dump(mode='json')) # Pydantic v2 uses model_dump()
    
    print(f"Created notebook document: {notebook_to_create.notebook_id} for user {user_id}")

    # 2. Create a Task document
    task_data = {
        "user_id": user_id,
        "tool_type": ToolType.NOTEBOOK_GENERATOR,
        "input_payload": {"topic": topic, "notebook_id": notebook_to_create.notebook_id},
        "status": TaskStatus.PENDING,
        "result_document_id": notebook_to_create.notebook_id,
        # task_id, created_at, updated_at will be set by TaskInDBBase default factories
    }
    task_to_create = TaskInDBBase(**task_data)

    # Save to Firestore
    task_ref = db.collection("tasks").document(task_to_create.task_id)
    # Storing tasks in a top-level collection for easier querying of all tasks
    task_ref.set(task_to_create.model_dump(mode='json'))
    print(f"Created task document: {task_to_create.task_id} for notebook {notebook_to_create.notebook_id}")

    # 3. Add the actual generation process to BackgroundTasks
    # This will call a function (e.g., from app.background.notebook_tasks)
    background_tasks.add_task(
        generate_notebook_content_task, 
        task_id=task_to_create.task_id, 
        user_id=user_id, 
        notebook_id=notebook_to_create.notebook_id, 
        topic=topic
    )
    print(f"Added background task for task_id: {task_to_create.task_id}, notebook_id: {notebook_to_create.notebook_id}")

    # Convert to the response models (Notebook and Task) which might have slightly different fields or representations if needed
    # In this case, NotebookInDBBase and TaskInDBBase are already suitable for returning
    created_notebook = Notebook(**notebook_to_create.model_dump())
    created_task = Task(**task_to_create.model_dump())

    return created_notebook, created_task

# Placeholder for other notebook service functions
async def get_notebook_by_id(notebook_id: str, user_id: str) -> Optional[Notebook]:
    db = get_firestore_client()
    notebook_ref = db.collection("users").document(user_id).collection("notebooks").document(notebook_id)
    doc = notebook_ref.get()
    if doc.exists:
        return Notebook(**doc.to_dict(), notebook_id=doc.id) # Pass doc.id if not stored in doc
    return None
