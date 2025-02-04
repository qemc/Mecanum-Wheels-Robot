from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()

# HTML for testing WebSockets
html = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Example</title>
</head>
<body>
    <h1>Video Stream</h1>
    <div>
        <textarea id="videoLog" rows="10" cols="50"></textarea><br>
    </div>
    <h1>Telemetry Data</h1>
    <div>
        <textarea id="telemetryLog" rows="10" cols="50"></textarea><br>
    </div>
    <script>
        // WebSocket for video stream
        const videoSocket = new WebSocket("ws://localhost:8000/video");
        videoSocket.onmessage = (event) => {
            const videoLog = document.getElementById("videoLog");
            videoLog.value += event.data + "\\n";
        };

        // WebSocket for telemetry data
        const telemetrySocket = new WebSocket("ws://localhost:8000/telemetry");
        telemetrySocket.onmessage = (event) => {
            const telemetryLog = document.getElementById("telemetryLog");
            telemetryLog.value += event.data + "\\n";
        };
    </script>
</body>
</html>
"""

# Endpoint to serve HTML
@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/video")
async def video_stream(websocket: WebSocket):
    await websocket.accept()  # Accept without checking origin
    try:
        while True:
            await websocket.send_text("Video frame data")
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print("Video WebSocket disconnected")

@app.websocket("/telemetry")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()  # Accept without checking origin
    try:
        while True:
            await websocket.send_text('{"pid_error": 0.02, "speed": 50}')


            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Telemetry WebSocket disconnected")
