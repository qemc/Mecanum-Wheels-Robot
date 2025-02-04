# main.py
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import depthai as dai
import numpy as np
import asyncio
import json
from shared_data import shared_pose_data  # Import the shared data structure
import math
import datetime

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

# Initialize DepthAI device
try:
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(30)

    xout = pipeline.createXLinkOut()
    xout.setStreamName("video")
    cam_rgb.preview.link(xout.input)

    device = dai.Device(pipeline)
    video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    print("DepthAI device initialized successfully.")
except Exception as e:
    print(f"Failed to initialize DepthAI device: {e}")
    video_queue = None  # Handle gracefully in WebSocket and HTTP endpoints

# ArUco parameters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
aruco_params = cv2.aruco.DetectorParameters()
marker_size = 0.08  # Marker size in meters (8x8 cm)

# Camera calibration parameters (example values, replace with your calibration data)
camera_matrix = np.array([
    [2972.01123046875, 0.0, 1937.57861328125],
    [0.0, 2972.01123046875, 1015.1455688476562],
    [0.0, 0.0, 1.0]
])
dist_coeffs = np.array([0, 0, 0, 0, 0])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Webpage for video and pose data."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArUco Pose Estimation</title>
    </head>
    <body>
        <h1>ArUco Pose Estimation</h1>
        <img src="/stream" style="border: 1px solid black; width: 640px; height: 480px;">
        <h3>Pose Data:</h3>
        <pre id="pose-data"></pre>
        <script>
            const ws = new WebSocket(`ws://${window.location.host}/pose`);
            ws.onopen = () => console.log("WebSocket connection established.");
            ws.onmessage = (event) => {
                console.log("Received pose data:", event.data);
                const data = JSON.parse(event.data);
                const formattedData = JSON.stringify(data, null, 4);  // 4-space indentation
                document.getElementById("pose-data").innerText = formattedData;
            };
            ws.onerror = (error) => console.error("WebSocket error:", error);
            ws.onclose = () => console.log("WebSocket connection closed.");
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/stream")
async def stream_video():
    """Stream video feed with ArUco markers."""
    if video_queue is None:
        error_message = "--frame\r\nContent-Type: text/plain\r\n\r\nDepthAI not initialized.\r\n"
        return StreamingResponse(iter([error_message]), media_type="multipart/x-mixed-replace; boundary=frame")

    def frame_generator():
        while True:
            try:
                frame = video_queue.get().getCvFrame()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

                if ids is not None:
                    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                        corners, marker_size, camera_matrix, None
                    )
                    for i in range(len(ids)):
                        cv2.aruco.drawDetectedMarkers(frame, corners)
                        # Draw coordinate axes for each detected marker
                        cv2.drawFrameAxes(frame, camera_matrix, None, rvecs[i], tvecs[i], 0.05)

                _, jpeg = cv2.imencode(".jpg", frame)
                frame_bytes = jpeg.tobytes()
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
            except Exception as e:
                print(f"Error in frame_generator: {e}")
                error_message = "--frame\r\nContent-Type: text/plain\r\n\r\nError processing frame.\r\n"
                yield (b"--frame\r\n"
                       b"Content-Type: text/plain\r\n\r\n" + error_message.encode() + b"\r\n")
                break

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/pose")
async def pose_websocket(websocket: WebSocket):
    """Send pose data over WebSocket including x, y, and rotation."""
    print("WebSocket connection attempt received.")
    try:
        await websocket.accept()
        print("WebSocket connection accepted.")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        return

    try:
        while True:
            if video_queue is None:
                pose_data = {"error": "DepthAI device not initialized."}
                await websocket.send_json(pose_data)
                print("DepthAI device not initialized. Sent error pose data.")
                await asyncio.sleep(1)
                continue

            try:
                frame = video_queue.get().getCvFrame()
            except Exception as e:
                print(f"Failed to retrieve frame from DepthAI: {e}")
                pose_data = {"error": "Failed to retrieve frame from DepthAI."}
                await websocket.send_json(pose_data)
                await asyncio.sleep(1)
                continue

            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)
            except Exception as e:
                print(f"Failed to process frame: {e}")
                pose_data = {"error": "Failed to process frame."}
                await websocket.send_json(pose_data)
                await asyncio.sleep(1)
                continue

            pose_data = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "pallet": None,
                "dropoff": None
            }

            if ids is not None:
                try:
                    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                        corners, marker_size, camera_matrix, None
                    )
                    for i, id in enumerate(ids.flatten()):
                        # Rotation vector in radians
                        rotation_rad = rvecs[i][0].tolist()
                        # Convert rotation vector to Euler angles (roll, pitch, yaw)
                        rotation_matrix, _ = cv2.Rodrigues(rvecs[i])
                        sy = math.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
                        singular = sy < 1e-6
                        if not singular:
                            roll = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
                            pitch = math.atan2(-rotation_matrix[2, 0], sy)
                            yaw = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
                        else:
                            roll = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
                            pitch = math.atan2(-rotation_matrix[2, 0], sy)
                            yaw = 0

                        # Convert radians to degrees
                        rotation_deg = {
                            "roll": round(math.degrees(roll), 2),
                            "pitch": round(math.degrees(pitch), 2),
                            "yaw": round(math.degrees(yaw), 2)
                        }

                        tvec = tvecs[i][0]  # Translation vector

                        # Extract only x and y positions
                        x = round(tvec[0], 2)  # in meters
                        y = round(tvec[1], 2)  # in meters

                        if id == 1:  # Pallet marker ID
                            pose_data["pallet"] = {
                                "orientation": rotation_deg,
                                "position": {
                                    "x": x,
                                    "y": y
                                }
                            }
                        elif id == 2:  # Drop-off marker ID
                            pose_data["dropoff"] = {
                                "orientation": rotation_deg,
                                "position": {
                                    "x": x,
                                    "y": y
                                }
                            }
                except Exception as e:
                    print(f"Failed to estimate pose: {e}")
                    pose_data["error"] = "Failed to estimate pose."

            print(f"Sending pose data: {pose_data}")
            await websocket.send_json(pose_data)

            # Update the shared pose data
            await shared_pose_data.update(pose_data)

            await asyncio.sleep(0.1)  # Limit update rate to 10Hz
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        print("WebSocket connection closed.")

@app.get("/pose_data")
async def get_pose_data():
    """HTTP GET endpoint to retrieve the latest pose data as JSON."""
    pose_data = await shared_pose_data.get_data()
    return pose_data

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"Failed to start Uvicorn server: {e}")
