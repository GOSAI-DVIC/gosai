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

        self.buffer = queue.Queue()

        def callback(outdata, frames, time, status):
            try:
                data = self.buffer.get_nowait()
            except queue.Empty:
                data = np.zeros(frames, dtype=np.float32)
            if len(data) < len(outdata):
                outdata[:len(data)] = np.array(data).reshape(-1,1)
                outdata[len(data):] = np.zeros(len(outdata) - len(data)).reshape(-1,1)
            else:
                outdata[:] = np.array(data).reshape(-1,1)


        DEVICE, SAMPLERATE, CHANNELS, BLOCKSIZE = get_speaker_configuration(self.parent.config)
        self.blocksize = BLOCKSIZE

        stream = sd.OutputStream(
            samplerate=SAMPLERATE, blocksize = BLOCKSIZE, callback=callback, channels=CHANNELS, device=DEVICE)
        stream.start()

        self.create_callback("play", self.play)
        self.create_callback("empty_buffer", self.empty_buffer)

    def play(self, data: List):
        """
        Plays the given data
        """
        blocks = len(data) // self.blocksize
        for i in range(blocks):
            self.buffer.put_nowait(data[i*self.blocksize:(i+1)*self.blocksize])
        self.buffer.put_nowait(data[blocks*self.blocksize:])

    def empty_buffer(self):
        """
        Empties the buffer
        """
        self.buffer = queue.Queue()
