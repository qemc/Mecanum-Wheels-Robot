from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import base64
import asyncio
from sharedData import shared_data
from initialization2 import initialize_all


# uvicorn backend:app --host 0.0.0.0 --port 8000


class ModeRequest(BaseModel):
    mode: str

async def app_lifespan(app: FastAPI):
    print("Starting up...")
    initialize_all()
    print("Ready")
    yield
    print("Shutting down...")

app = FastAPI(lifespan=app_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/mode")
async def get_mode():
    try:
        current_mode = shared_data.get_mode()
        return {"mode": current_mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mode: {str(e)}")

@app.post("/mode")
async def set_mode(mode_request: ModeRequest):
    try:
        shared_data.set_mode(mode_request.mode)
        return {"status": "success", "mode": mode_request.mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set mode: {str(e)}")

@app.websocket("/video")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    print("Video client connected")
    
    try:
        while True:
            frame = shared_data.get_frame()
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                data = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
                await websocket.send_text(data)
            await asyncio.sleep(0.2)
            
    except WebSocketDisconnect:
        print("Video client disconnected")
    except Exception as e:
        print(f"Video error: {str(e)}")

last_pose_data = None

@app.websocket("/pose")
async def pose_stream(websocket: WebSocket):
    global last_pose_data
    await websocket.accept()
    print("Pose client connected")
    
    try:
        while True:
            data = shared_data.get_pose_data()
            if data != last_pose_data:
                await websocket.send_json(data)
                last_pose_data = data
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        print("Pose client disconnected")
    except Exception as e:
        print(f"Pose error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)