from fastapi import FastAPI
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import API routes
from api.routes import app as api_app
from fastapi.middleware.cors import CORSMiddleware

# Load configuration settings
from config import settings

# Initialize FastAPI app
app = FastAPI(title="Call Summarization API")

# Apply CORS middleware (Corrected)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change as needed)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create required directories if they don’t exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.PROCESSED_FOLDER, exist_ok=True)
os.makedirs(settings.REPORTS_FOLDER, exist_ok=True)

# Include API routes (directly, instead of using `mount`)
app.include_router(api_app.router)

# Health check endpoint
@app.get("/health_check/")
def health_check():
    """Simple health check endpoint."""
    return {"status": "API is running smoothly!"}

# Entry point to run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=True)
