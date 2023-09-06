from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample

class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        #create driver event
        self.register_to_driver("microphone", "audio_stream")

        self.create_event("frequency")

        self.MAX_FREQUENCY = 2100

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.blocks = []

        self.create_callback_on_event("estimate_frequency", self.estimate_frequency, "microphone", "audio_stream")

    def estimate_frequency(self, data):
        """Estimates the frequency of the input data"""

        block = data["block"][:, 0]

        if len(self.blocks) < 8*len(block):
            self.blocks.extend(block)
        else:
            self.blocks = self.blocks[len(block):]
            self.blocks.extend(block)
        samplerate = data["samplerate"]
        rfft = np.abs(np.fft.rfft(self.blocks))
        freq = np.fft.rfftfreq(2*len(rfft)-1, 1/samplerate)

        self.set_event_data("frequency", {
            "max_frequency": freq[np.argmax(rfft)],
            "rfft": list(rfft[freq<self.MAX_FREQUENCY]),
            "amplitude": np.max(rfft),
            "blocksize": len(block),
        })
