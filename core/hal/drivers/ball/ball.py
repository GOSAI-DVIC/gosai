# Balls estimation Driver
# Return a list containing x,y ball positions

import time

import core.hal.drivers.ball.utils.ball_detection as bd
from core.hal.drivers.driver import BaseDriver

class Driver(BaseDriver):
    
    def __init__(self, name: str, parent, max_fps: int = 120):
        super().__init__(name, parent)

        self.camera_data, self.empty_bg = bd.init()
        self.paused = False

        self.register_to_driver("video", "color")

        self.create_event("ball_data")

        self.fps = max_fps

    def loop(self):  
        start_t = time.time()
        color = self.parent.get_driver_event_data("video","color")
        if color is not None:
            ball_data = bd.BallDetection(
                self.empty_bg, 
                color, #to get a frame
                self.camera_data
            ) #it returns l
            self.set_event_data("ball_data",ball_data)
            # print(ball_data)
            
        dt = max(1 / self.fps - (time.time() - start_t), 0.0001)
        # print(1/(time.time()-start_t))
        time.sleep(dt)