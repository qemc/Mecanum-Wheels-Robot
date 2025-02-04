# app/pose_websocket.py
from fastapi import APIRouter, WebSocket
from shared_data import shared_pose_data
from camera import get_frame
from aruco_detection import detect_aruco_markers
import asyncio
import datetime
import logging

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

@router.websocket("/pose")
async def pose_websocket(websocket: WebSocket):
    """Send pose data over WebSocket including x, y, and rotation."""
    await websocket.accept()
    logger.info("WebSocket connection accepted.")

    try:
        while True:
            frame = await get_frame()
            if frame is None:
                pose_data = {"error": "DepthAI device not initialized."}
                await websocket.send_json(pose_data)
                logger.warning("DepthAI device not initialized. Sent error pose data.")
                await asyncio.sleep(1)
                continue

            try:
                pose_data = detect_aruco_markers(frame)
                pose_data["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
            except Exception as e:
                logger.error(f"Failed to process frame: {e}")
                pose_data = {"error": "Failed to process frame."}

            logger.info(f"Sending pose data: {pose_data}")
            await websocket.send_json(pose_data)

            # Update the shared pose data
            await shared_pose_data.update(pose_data)

            await asyncio.sleep(0.1)  # Limit update rate to 10Hz
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        logger.info("WebSocket connection closed.")
