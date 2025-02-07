# backend.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import base64
import asyncio
from sharedData import shared_data
from initialization import initialize_all


# uvicorn backend:app --host 0.0.0.0 --port 8000

class PickingProcessRequest(BaseModel):
    picking_process: bool
    

async def app_lifespan(app: FastAPI):
    initialize_all()
    yield

app = FastAPI(lifespan=app_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


    
@app.websocket("/runPick")
async def handle_picking(ws: WebSocket):
    await ws.accept()
    print("Picking Handler WebSocket connected")

    async def send_updates():
        """Send updates to the frontend at regular intervals."""
        last_status = None
        last_start_picking_process = None
        while True:
            
            current_status = shared_data.get_picking_status()
            current_start_picking_process = shared_data.get_start_picking_process()

            if (current_status != last_status) or (current_start_picking_process != last_start_picking_process):
                
                data_to_send = {
                    'status': current_status,
                    'start_picking_process': current_start_picking_process
                }
                await ws.send_json(data_to_send)
                print("Sent to frontend:", data_to_send)

                last_status = current_status
                last_start_picking_process = current_start_picking_process

            await asyncio.sleep(0.5) 

    async def receive_messages():

        while True:
            try:
                new_data = await ws.receive_json()
                if "start_picking_process" in new_data:
                    shared_data.set_start_picking_process(new_data["start_picking_process"])
                    print("Received from frontend:", new_data)
                    
            except WebSocketDisconnect:
                print("Picking Handler disconnected")
                break
            
            except Exception as e:
                print(f"Picking Handler Error: {e}")
                break

    try:
        await asyncio.gather(send_updates(), receive_messages())
    except WebSocketDisconnect:
        print("Picking Handler WebSocket disconnected")

        
@app.websocket("/mode")
async def handle_mode_selection(ws: WebSocket):
    
    await ws.accept()
    print("Mode Handler Websocket connected")
    
    try:
        while True:
            
            current_mode = shared_data.get_mode()
                
            await ws.send_json({
                'mode': current_mode
            })
            
            new_mode = await ws.receive_json()
            shared_data.set_mode(new_mode.get("mode"))
            
    except WebSocketDisconnect:
        print("Mode Handler disconnected")
    except Exception as e:
        print(f"Mode Handler Error: {e}")
        
        
@app.websocket("/forklift")
async def forklift_control(ws: WebSocket):
    await ws.accept()
    print("Forklift WebSocket connected")

    async def send_updates():
        """Send updates to the frontend at regular intervals."""
        last_state = None
        while True:
            current_state = {
                'command_up': shared_data.get_forklift_command_up(),
                'command_down': shared_data.get_forklift_command_down(),
                'status': shared_data.get_forklift_status(),
                'zero': shared_data.get_forklift_zero()
            }

            if current_state != last_state:
                await ws.send_json(current_state)
                print("Sent to frontend:", current_state)
                last_state = current_state

            await asyncio.sleep(0.5)  
            
    async def receive_commands():
        """Receive and process commands from the frontend."""
        while True:
            try:
                new_command = await asyncio.wait_for(ws.receive_json(), timeout=1.0)
                print("Received from frontend:", new_command)

                new_command_up = new_command.get('command_up')
                new_command_down = new_command.get('command_down')
                new_command_zero = new_command.get('zero')

                current_status = shared_data.get_forklift_status()
                current_mode = shared_data.get_mode()

                if current_status == 'Steady up' and current_mode == 'manual':
                    shared_data.set_forklift_command_down(new_command_down)

                elif current_status == 'Steady down' and current_mode == 'manual':
                    shared_data.set_forklift_command_up(new_command_up)

                if new_command_zero:
                    shared_data.set_forklift_zero(new_command_zero)

            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                print("Forklift WebSocket disconnected")
                break
            except Exception as e:
                print(f"Forklift WebSocket Error (receive): {e}")
                break

    try:
        await asyncio.gather(send_updates(), receive_commands())
    except WebSocketDisconnect:
        print("Forklift WebSocket disconnected")
    except Exception as e:
        print(f"Forklift WebSocket Error: {e}")
        

@app.websocket("/video")
async def video_stream(ws: WebSocket):
    
    await ws.accept()
    print("Video client connected")
    
    try:
        while True:
            frame = shared_data.get_frame()
            
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                data = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
                await ws.send_text(data)
                
            await asyncio.sleep(0.2)
            
    except WebSocketDisconnect:
        print("Video client disconnected")
        
    except Exception as e:
        print(f"Video error: {e}")
        
        


@app.websocket("/pose")
async def pose_stream(ws: WebSocket):
    
    await ws.accept()
    print("Pose client connected")
    
    try:
        while True:
            data = shared_data.get_pose_data()
            
            await ws.send_json(data)
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        print("Pose client disconnected")
        
    except Exception as e:
        print(f"Pose error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

