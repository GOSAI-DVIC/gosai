import math
from core.hal.drivers.driver import BaseDriver
import sounddevice as sd
import queue
import numpy as np


class Driver(BaseDriver):
    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        # create driver event
        self.create_event("get_audio_stream")


    def pre_run(self):
        # runs to do at the start of the driver
        BLOCKSIZE = 1024  # TODO:read these parameters from config.json
        SAMPLERATE = 48000
        CHANNELS = 1
        DEVICE = 6

        if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                CHANNELS = config["microphone"]["channels_nb"] if ("channels_nb" in config["microphone"]) else 1

                if ("number" in config["microphone"]):
                    DEVICE = config["microphone"]["number"]
        
        else: 
            CHANNELS = 1
            DEVICE = 6

        def callback(indata, frames, time, status):
            self.set_event_data(
                "get_audio_stream",
                {
                    "block": indata,
                    "samplerate": SAMPLERATE,
                },
            )

        stream = sd.InputStream(
            samplerate=SAMPLERATE,
            blocksize=BLOCKSIZE,
            callback=callback,
            channels=CHANNELS,
            device=DEVICE,
        )

        stream.start()
