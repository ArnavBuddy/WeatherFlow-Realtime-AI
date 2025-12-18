import asyncio
import websockets
import uuid

async def test_connection():
    session_id = str(uuid.uuid4())
    uri = f"ws://127.0.0.1:8000/ws/session/{session_id}"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            await websocket.send("Hello")
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
