import asyncio, websockets, json

async def test():
    uri = "ws://127.0.0.1:8000/ws"
    async with websockets.connect(uri) as ws:
        # Step 1: Wait for connection message
        response = await ws.recv()
        print("Got:", response)

        # Step 2: Send a test frame request
        await ws.send(json.dumps({"frame_id": "test123"}))

        # Step 3: Wait for match response
        response = await ws.recv()
        print("Got:", response)

asyncio.run(test())
