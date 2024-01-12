import tornado.ioloop
import tornado.web
import tornado.websocket
import pandas as pd

# Prepare data for streaming over and over
df = pd.read_parquet('yellow_tripdata_2023-01.parquet', engine='fastparquet')
data_array = df.to_numpy()
print("DATA IS READY CALL THE CLIENT!")

class StreamMessagesHandler(tornado.websocket.WebSocketHandler):
    async def open(self):
        print("WebSocket opened")

    async def on_message(self, message):
        if message == "Start!": 
            print("SERVER GOT THE START MESSAGE")
            # Stream all the data over and over
            i = 0
            while True:
                await self.write_message(str(data_array[i]))
                i = (i + 1) % len(data_array)

    def on_close(self):
        print("WebSocket closed")

app = tornado.web.Application([
    (r"/websocket", StreamMessagesHandler),
])

def main():
    app.listen(8888)
    print("Starting Tornado Web server on port 8888")
    tornado.ioloop.IOLoop.current().start()

# Running the server
if __name__ == "__main__":
    main()
