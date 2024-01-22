# Hand Pose estimation Driver

import time
import asyncio
import websockets
import json
from PIL import Image
import io
import time
import pickle
import numpy as np

from core.hal.drivers.driver import BaseDriver

uri = "ws://10.8.0.11:8080/ws/image2image"

class Driver(BaseDriver):
    """sdxl api interface driver"""
    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.create_event("response")
        self.socket = None

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()


    async def handle_images(self):
        try:
            async with websockets.connect(uri, ping_interval=None, ping_timeout=None, close_timeout=300) as websocket:
                # get image from redis
                redis_read=self.db.get("sdxl_api")
                if redis_read is None:
                    print("redis_read is None")
                    return
                redis_payload = redis_read
                # print("redis_payload", redis_payload)
                start = time.time()
                # Send data
                await websocket.send(redis_payload)
                middle = time.time()
                # Wait for the response (binary data)
                response_bytes = await websocket.recv()
                end = time.time()
                self.set_event_data("response", response_bytes)
                # print("sdxl_api", response_bytes)
                print("sending: ", middle - start)
                print("receiving: ", end - middle)
                print("total: ", end - start)
        except Exception as e:
            print("sdxl_api exception", e)
            time.sleep(1)
            # pass
    
    def loop(self):
        """Runs in a loop for the driver"""
        super().loop()
        asyncio.get_event_loop().run_until_complete(self.handle_images())
        # time.sleep(1 / self.fps)  # Runs faster to be sure to get the current frame
        # print("sdxl_api loop")
        # self.set_event_data("response", "sdxl_api response")
        # print("sdxl_api response")