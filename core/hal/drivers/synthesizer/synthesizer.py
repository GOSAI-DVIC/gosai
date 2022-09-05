import math
from core.hal.drivers.driver import BaseDriver
import sounddevice as sd
import queue
import numpy as np


class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        #create driver event
        self.create_event("synthesizing")
        self.create_callback("play_synth", self.play_synth)
        
    # def pre_run(self):
        # runs to do at the start of the driver
        self.buffer_queue = queue.Queue(3)

        def callback(outdata, frames, time, status):
            try:
                data = self.buffer_queue.get_nowait()
            except queue.Empty:
                data = np.zeros(frames, dtype=np.float32)
            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = np.zeros(len(outdata) - len(data))
            else:
                outdata[:] = data.reshape(-1,1)
        
        self.stream = sd.OutputStream(
            samplerate=48000, blocksize=2048, callback=callback, channels=1)
        self.stream.start()
        self.phase = 0

    def play_synth(self, data):
        bitrate = max(data["bitrate"], data["frequency"]+100)
        frequency = data["frequency"]
        amplitude = data["amplitude"]
        numberofframes = int(data["bitrate"] * data["length"])
        WAVEDATA = [amplitude * math.sin(2*math.pi*frequency*x/bitrate + self.phase) for x in range(2048)]
        try:
            self.buffer_queue.put_nowait(np.array(WAVEDATA, dtype=np.float32))
            self.phase = (2*math.pi*frequency*2047/bitrate + self.phase) % (2*math.pi)
        except:
            pass
        