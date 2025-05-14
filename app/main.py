from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.endpoints import notebooks, tasks
from app.core.config import settings
from app.db.firestore import initialize_firebase_admin, get_firestore_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application startup...")
    initialize_firebase_admin()
    # You can also test the client connection here if needed
    # try:
    #     client = get_firestore_client()
    #     # Perform a simple operation like listing collections (requires specific permissions)
    #     # or getting a non-existent document to check connectivity without altering data.
    #     print("Firestore client obtained during startup.")
    # except Exception as e:
    #     print(f"Error obtaining Firestore client during startup: {e}")
    yield
    # Shutdown
    print("Application shutdown...")
    # Clean up resources if needed, though firebase_admin usually manages its own connection pool.

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# API Routers
app.include_router(notebooks.router, prefix=settings.API_V1_STR + "/notebooks", tags=["Notebooks"])
app.include_router(tasks.router, prefix=settings.API_V1_STR + "/tasks", tags=["Tasks"])

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
