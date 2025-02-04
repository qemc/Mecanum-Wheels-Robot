# app/video_stream.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
import asyncio
from config import video_queue
from aruco_detection import detect_aruco_markers
import logging

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize DepthAI device and get the video queue


@router.get("/stream")
async def stream_video():
    """Stream video feed with ArUco markers."""
    if video_queue is None:
        error_message = "--frame\r\nContent-Type: text/plain\r\n\r\nDepthAI not initialized.\r\n"
        return StreamingResponse(iter([error_message]), media_type="multipart/x-mixed-replace; boundary=frame")

    def frame_generator():
        while True:
            try:
                frame = video_queue.get().getCvFrame()
                pose_data = detect_aruco_markers(frame)
                # Optionally, handle pose_data here (e.g., log or store)
                _, jpeg = cv2.imencode(".jpg", frame)
                frame_bytes = jpeg.tobytes()
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
            except Exception as e:
                logger.error(f"Error in frame_generator: {e}")
                error_message = "--frame\r\nContent-Type: text/plain\r\n\r\nError processing frame.\r\n"
                yield (b"--frame\r\n"
                       b"Content-Type: text/plain\r\n\r\n" + error_message.encode() + b"\r\n")
                break

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")
