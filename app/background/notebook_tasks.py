import time
import asyncio
from app.db.firestore import get_firestore_client
from app.models.notebook import NotebookStatus, NotebookUpdate, ImageRequest
from app.models.task import TaskStatus, TaskUpdate
from datetime import datetime
import re

from app.services.ai.llm import llm_service
from app.services.ai.image_scraper import image_scraper_service
from app.services.ai.image_validator import image_validator_service # Import the new image validator service

def update_notebook_status(db, user_id: str, notebook_id: str, status: NotebookStatus, error_message: str = None):
    notebook_ref = db.collection("users").document(user_id).collection("notebooks").document(notebook_id)
    update_data = {"status": status.value, "updated_at": datetime.utcnow()}
    if error_message: update_data["error_message"] = error_message
    notebook_ref.update(update_data)
    print(f"Notebook {notebook_id} status updated to {status.value}")

def update_task_status(db, task_id: str, status: TaskStatus, error_message: str = None):
    task_ref = db.collection("tasks").document(task_id)
    update_data = {"status": status.value, "updated_at": datetime.utcnow()}
    if error_message: update_data["error_message"] = error_message
    task_ref.update(update_data)
    print(f"Task {task_id} status updated to {status.value}")

async def generate_notebook_content_task(task_id: str, user_id: str, notebook_id: str, topic: str):
    print(f"[TASK_STARTED_ASYNC] Task ID: {task_id}, Notebook ID: {notebook_id}, User ID: {user_id}, Topic: {topic}")
    db = get_firestore_client()

    try:
        update_task_status(db, task_id, TaskStatus.PROCESSING)
        update_notebook_status(db, user_id, notebook_id, NotebookStatus.PROCESSING_TEXT)
        
        llm_output_with_placeholders = await llm_service.generate_text_with_image_cues(topic)
        
        notebook_ref = db.collection("users").document(user_id).collection("notebooks").document(notebook_id)
        notebook_ref.update({
            "llm_generated_text_with_placeholders": llm_output_with_placeholders,
            "updated_at": datetime.utcnow()
        })
        print(f"LLM text generated for notebook {notebook_id}.")

        image_queries = []
        for match in re.finditer(r"image - \[(.*?)\]", llm_output_with_placeholders):
            image_queries.append(match.group(1))

        processed_image_requests = []

        if image_queries:
            update_notebook_status(db, user_id, notebook_id, NotebookStatus.PROCESSING_IMAGES)
            print(f"Processing {len(image_queries)} image queries: {image_queries}")
            
            for query in image_queries:
                current_image_request = ImageRequest(query=query, status="PENDING")
                try:
                    scraped_urls = await image_scraper_service.scrape_images(query, count=1)
                    
                    if scraped_urls:
                        current_image_request.original_url = scraped_urls[0]
                        current_image_request.status = "FETCHED"
                        print(f"Image fetched for '{query}': {current_image_request.original_url}")
                        
                        # *** Call the image validator service ***
                        is_valid, validated_url = await image_validator_service.validate_image(
                            image_url=current_image_request.original_url,
                            text_context=llm_output_with_placeholders, # Pass full text for context
                            query_context=query
                        )

                        if is_valid and validated_url:
                            current_image_request.validated_image_url = validated_url
                            current_image_request.status = "VALIDATED"
                            print(f"Image validated for '{query}': {current_image_request.validated_image_url}")
                        else:
                            current_image_request.status = "FAILED"
                            current_image_request.error_message = "Image validation failed or not suitable"
                            print(f"Image validation failed for '{query}'. Reason (mocked): Not suitable.")
                    else:
                        current_image_request.status = "FAILED"
                        current_image_request.error_message = "No images found by scraper"
                        print(f"No images found by scraper for '{query}'")
                
                except Exception as img_exc:
                    print(f"Error processing image query '{query}': {img_exc}")
                    current_image_request.status = "FAILED"
                    current_image_request.error_message = str(img_exc)
                
                processed_image_requests.append(current_image_request.model_dump(mode='json'))
            
            notebook_ref.update({"image_requests": processed_image_requests, "updated_at": datetime.utcnow()})
            print(f"Image processing phase completed for notebook {notebook_id}")
        else:
            print(f"No image placeholders found in notebook {notebook_id}")

        final_content = llm_output_with_placeholders
        for img_req_data in processed_image_requests:
            if img_req_data.get("status") == "VALIDATED" and img_req_data.get("validated_image_url"):
                placeholder = f"image - [{img_req_data['query']}]"
                image_embed_code = f"![{img_req_data['query']}]({img_req_data['validated_image_url']})" # Markdown
                final_content = final_content.replace(placeholder, image_embed_code, 1)
            # else: # Optionally handle failed/unvalidated images, e.g. remove placeholder or add a note
                # placeholder = f"image - [{img_req_data['query']}]"
                # final_content = final_content.replace(placeholder, "[Image not available]", 1)

        notebook_ref.update({"final_content": final_content, "updated_at": datetime.utcnow()})
        print(f"Final content assembled for notebook {notebook_id}")

        update_notebook_status(db, user_id, notebook_id, NotebookStatus.COMPLETED)
        update_task_status(db, task_id, TaskStatus.COMPLETED)
        print(f"[TASK_COMPLETED_ASYNC] Notebook {notebook_id} generation successful.")

    except Exception as e:
        print(f"[TASK_FAILED_ASYNC] Error during notebook generation for task {task_id}, notebook {notebook_id}: {e}")
        import traceback
        traceback.print_exc()
        error_message = str(e)
        try:
            update_notebook_status(db, user_id, notebook_id, NotebookStatus.FAILED, error_message=error_message)
            update_task_status(db, task_id, TaskStatus.FAILED, error_message=error_message)
        except Exception as db_update_e:
            print(f"Critical: Failed to update statuses to FAILED for task {task_id}, notebook {notebook_id}: {db_update_e}")
