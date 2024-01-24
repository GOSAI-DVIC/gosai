import numpy  # Make sure NumPy is loaded before it is used in the callback
import sounddevice as sd
import time as tm 

from core.hal.drivers.driver import BaseDriver
from core.hal.drivers.microphone.utils.microphone_finder import get_microphone_configuration

assert numpy  # avoid "imported but unused" message (W0611)

class Driver(BaseDriver):
    def __init__(self, name: str, parent):
        super().__init__(name, parent)
        # create driver event
        self.create_event("audio_stream")


    def pre_run(self):
        # runs to do at the start of the driver
        DEVICE, SAMPLERATE, CHANNELS, BLOCKSIZE = get_microphone_configuration(self.parent.config)
        def callback(indata, frames, time, status) -> None:
            
            self.set_event_data(
                "audio_stream",
                {
                    "block": indata[:],
                    "samplerate": SAMPLERATE,
                    "timestamp": tm.time(),
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
