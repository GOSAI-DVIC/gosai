import queue
from typing import List

import numpy as np
import sounddevice as sd

from core.hal.drivers.driver import BaseDriver
from core.hal.hal import HardwareAbstractionLayer
from core.hal.drivers.speaker.utils.device_detection import get_speaker_configuration


class Driver(BaseDriver):
    """
    Speaker driver, can play audio data from list of -1 to 1 floats
    """

    def __init__(self, name: str, parent: HardwareAbstractionLayer):
        super().__init__(name, parent)

        self.buffer: queue.Queue = None
        self.blocksize: int = None

    def pre_run(self):
        super().pre_run()

        self.create_event("settings")
        self.create_callback("play", self.play)
        self.create_callback("empty_buffer", self.empty_buffer)

        DEVICE, SAMPLERATE, CHANNELS, BLOCKSIZE = get_speaker_configuration(self.parent.config)
        self.set_event_data("settings", {
            "device": DEVICE,
            "samplerate": SAMPLERATE,
            "channels": CHANNELS,
            "blocksize": BLOCKSIZE,
        })

        self.buffer = queue.Queue()

        def callback(outdata, frames, time, status):
            if not self.buffer.empty():
                data = self.buffer.get()
            else:
                data = np.zeros(frames, dtype=np.float32)
            outdata[:] = np.array(data).reshape(-1,1)


        self.blocksize = BLOCKSIZE

        stream = sd.OutputStream(
            samplerate=SAMPLERATE, blocksize = BLOCKSIZE, callback=callback, channels=CHANNELS, device=DEVICE)
        stream.start()

    def play(self, data: np.ndarray):
        """
        Add the given data to the play buffer. If the data is smaller than the blocksize, it will be padded with zeros!
        """
        if len(data.shape) > 1:
            data = data.reshape(-1)

        i = 0
        data_size = data.shape[0]

        while i < data_size:
            size = min(data_size - i, self.blocksize )
            b = data[i:i+size]
            if size < self.blocksize:
                b = np.append(b, np.zeros(self.blocksize - size))
            self.buffer.put(b)
            i += size

    def empty_buffer(self):
        """
        Empties the buffer
        """
        self.buffer = queue.Queue()
