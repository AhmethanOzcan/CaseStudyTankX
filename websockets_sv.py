import asyncio
import websockets
import pandas as pd

# Prepare data for streaming over and over
df = pd.read_parquet('yellow_tripdata_2023-01.parquet', engine='fastparquet')
data_array = df.to_numpy()
print("DATA IS READY CALL THE CLIENT!")

async def stream_messages(websocket, path):
    while True:

        print("SERVER WAITING FOR START MESSAGE")
        # Wait till get the start message from connected websocket client
        while True:
            message = await websocket.recv()
            if message == "Start!": break
        print("SERVER GOT THE START MESSAGE")

        # Stream all the data over and over
        i = 0
        while True:
            await websocket.send(str(data_array[i]))
            i = (i + 1) % len(data_array)

async def main():
    start_server = await websockets.serve(stream_messages, "localhost", 8080)
    await start_server.wait_closed()

# Running the server
asyncio.run(main())