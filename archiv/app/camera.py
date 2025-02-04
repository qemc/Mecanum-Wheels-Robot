# app/camera.py
from config import video_queue
import logging

logger = logging.getLogger(__name__)



async def get_frame():
    if video_queue is None:
        logger.error("Video queue is not initialized.")
        return None
    try:
        frame = video_queue.get().getCvFrame()
        return frame
    except Exception as e:
        logger.error(f"Failed to retrieve frame from DepthAI: {e}")
        return None
