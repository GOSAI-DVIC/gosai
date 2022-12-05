# Sensor Server Driver

import numpy as np
import socket
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """Sensor Server driver"""
    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)

        self.create_event("movements")
        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps
        self.window = 1

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()
        s = socket.socket()
        s.bind(('172.21.72.142', 8090))
        s.listen(0)

        try:
            self.client, self.addr = s.accept()
            print('Got connection from', self.addr)
        except:
            print('Connection failed')


    def loop(self):
        """Main loop"""
        content = self.client.recv(32)
        print(content)
        self.set_event_data("movements", int(content))

        if self.debug_data:
                self.log(content)
        

        