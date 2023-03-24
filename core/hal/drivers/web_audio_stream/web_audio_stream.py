# Video driver
import json
import os
import sys
import time
from os import path

from core.hal.drivers.driver import BaseDriver
import numpy as np 



class Driver(BaseDriver):
   
    def __init__(
        self, name: str, parent, fps: int = 30
    ): 
        super().__init__(name, parent)

        self.type = "no_loop"
        self.samplerate = 44100
        self.audio_type = "float32"
        self.create_event("web_audio_1sec")
        self.create_callback("audio_conversion", self.audio_conversion)
        self.log("pre_run", 3)
      
       
    def audio_conversion(self, data):  

        audio_data = data["data"]      
        bytes = audio_data['bytes']
        
        self.log("audio_conversion", 3)
        float32buffer = np.frombuffer(bytes, dtype=np.float32)
        databuffer = np.append(databuffer,float32buffer)
   
        if databuffer.size > self.samplerate:

            datafor1sec = databuffer[:self.samplerate]
            
            print(datafor1sec)
            self.set_event_data("web_audio_1sec", datafor1sec)
          
            databuffer = databuffer[self.samplerate:]
       
