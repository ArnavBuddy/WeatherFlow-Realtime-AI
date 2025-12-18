from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from app.services.session_manager import session_manager
from app.services.processing_service import process_session_summary
import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    # Serve index.html (or redirect)
    # For simplicity, we can just tell user to go to /static/index.html
    # or serve it directly
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, background_tasks: BackgroundTasks):
    # Note: background_tasks in WS is tricky because WS is long lived and BTs run after response.
    # But here we want the task triggered AFTER WS disconnect.
    # FastAPI BackgroundTasks are for HTTP responses usually. 
    # For WS, we can just use asyncio.create_task()
    
    await session_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            await session_manager.handle_message(session_id, data)
    except WebSocketDisconnect:
        duration = await session_manager.disconnect(session_id)
        # Trigger background task
        import asyncio
        asyncio.create_task(process_session_summary(session_id, duration))
