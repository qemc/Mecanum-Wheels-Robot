# app/main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

# Import routers from other modules
from video_stream import router as video_stream_router
from pose_websocket import router as pose_websocket_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS (optional, adjust origins as needed)
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://192.168.137.76:8000",
    # Add other origins if accessing from different domains or devices
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video_stream_router)
app.include_router(pose_websocket_router)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Webpage for video and pose data."""
    return templates.TemplateResponse("index.html", {"request": request})

# Run the app if this file is executed directly
if __name__ == "__main__":
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Failed to start Uvicorn server: {e}")
