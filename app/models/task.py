from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import uuid

# Enum for Task Status
class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# Enum for Tool Type
class ToolType(str, enum.Enum):
    NOTEBOOK_GENERATOR = "notebook_generator"
    STORY_BOOK_GENERATOR = "story_book_generator"
    # Add other tool types here in the future

class TaskBase(BaseModel):
    user_id: str
    tool_type: ToolType
    input_payload: Dict[str, Any] # e.g., {"topic": "user's topic"} for notebook

class TaskCreate(TaskBase):
    pass

class TaskInDBBase(TaskBase):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    # This ID will point to the document created by the task, e.g., a notebookId or storyId
    result_document_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    """
    Represents a Task document as stored in Firestore and returned to the client.
    """
    pass

class TaskUpdate(BaseModel):
    """
    Model for updating parts of a task document.
    All fields are optional.
    """
    status: Optional[TaskStatus] = None
    result_document_id: Optional[str] = None
    error_message: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
