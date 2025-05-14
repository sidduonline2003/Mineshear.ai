from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid

# Enums for status fields
class NotebookStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING_TEXT = "PROCESSING_TEXT"
    PROCESSING_IMAGES = "PROCESSING_IMAGES"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ImageRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    FETCHED = "FETCHED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"
    # SKIPPED might also be a useful status if an image is optional or cannot be found

class ImageRequest(BaseModel):
    query: str
    status: ImageRequestStatus = Field(default=ImageRequestStatus.PENDING)
    original_url: Optional[str] = None # URL from scraper
    validated_image_url: Optional[str] = None # URL after validation
    error_message: Optional[str] = None
    # Potential future fields: source_api, license_info

class NotebookBase(BaseModel):
    topic_input: str
    user_id: str # To associate with the user who created it

class NotebookCreate(NotebookBase):
    pass # Fields from NotebookBase are inherited

class NotebookInDBBase(NotebookBase):
    notebook_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: NotebookStatus = Field(default=NotebookStatus.PENDING)
    llm_generated_text_with_placeholders: Optional[str] = None
    image_requests: List[ImageRequest] = Field(default_factory=list)
    final_content: Optional[str] = None # Markdown or HTML
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True # Allows creating from ORM models or dicts with attribute access
        # For FastAPI, an alias generator can be useful for camelCase JSON and snake_case Python
        # def to_camel(string: str) -> str:
        #     return ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(string.split('_')))
        # alias_generator = to_camel


class Notebook(NotebookInDBBase):
    '''
    Represents a Notebook document as stored in Firestore and returned to the client.
    '''
    pass

class NotebookUpdate(BaseModel):
    '''
    Model for updating parts of a notebook document.
    All fields are optional.
    '''
    topic_input: Optional[str] = None
    status: Optional[NotebookStatus] = None
    llm_generated_text_with_placeholders: Optional[str] = None
    image_requests: Optional[List[ImageRequest]] = None
    final_content: Optional[str] = None
    error_message: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Example usage (not part of the file, just for illustration):
# if __name__ == "__main__":
#     img_req = ImageRequest(query="A cute cat", status=ImageRequestStatus.PENDING)
#     print(img_req.model_dump_json(indent=2))

#     notebook_data = {
#         "topic_input": "The future of AI",
#         "user_id": "user123",
#         "notebook_id": "nb_abc123",
#         "status": NotebookStatus.PROCESSING_TEXT,
#         "llm_generated_text_with_placeholders": "AI is evolving. image - [An advanced AI robot]",
#         "image_requests": [img_req.model_dump()],
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }
#     notebook_doc = Notebook(**notebook_data)
#     print(notebook_doc.model_dump_json(indent=2))
#     notebook_doc.image_requests[0].status = ImageRequestStatus.FETCHED
#     notebook_doc.updated_at = datetime.utcnow()
#     print(notebook_doc.model_dump(mode='json')['image_requests'][0]['status']) # Accessing enum value
#     print(NotebookStatus.COMPLETED.value)
