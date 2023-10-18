from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
import samplerate
import torch
import numpy as np 
import sys
import os 
# import webrtcvad

class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)
        self.create_event("activity")

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()


        self.sr = 16000
        self.model, self.utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                    model='silero_vad',
                                    force_reload=True)

        
        self.create_callback("predict", self.predict)


    def predict(self, data : dict):
        """
        data["activity_buffer"] : audio list
            -> float32
            -> 16000Hz
        
        """
        ## Outputs activity probablitily
        audio = torch.Tensor(data["activity_buffer"])
        speech_prob = self.model(audio, self.sr).item()
      
        #Send it back to the application
        self.set_event_data(
            "activity",
            {
                "confidence": speech_prob,
            },
        )
        #return speech_prob


