from cmath import isnan
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
        self.create_callback("play", self.play)
        self.create_callback("add_to_queue", self.add_to_queue)
        self.create_callback("empty_queue", self.empty_queue)
        self.blocksize = 2048
        self.sample_rate = 48000
        
    # def pre_run(self):
        # runs to do at the start of the driver
        self.buffer = queue.Queue(3)
        self.queue = queue.Queue()

        def callback_live(outdata, frames, time, status):
            try:
                data = self.buffer.get_nowait()
            except queue.Empty: 
                data = np.zeros(frames, dtype=np.float32)
            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = np.zeros(len(outdata) - len(data))
            else:
                outdata[:] = data.reshape(-1,1)
        
        self.live_stream = sd.OutputStream(
            samplerate=48000, blocksize = self.blocksize, callback=callback_live, channels=1)
        self.live_stream.start()
        self.buffer_phase = 0

        def callback_playback(outdata, frames, time, status):
            try:
                data = self.queue.get_nowait()
            except queue.Empty:
                data = np.zeros(frames, dtype=np.float32)
            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = np.zeros(len(outdata) - len(data))
            else:
                outdata[:] = data.reshape(-1,1)
        
        self.stream = sd.OutputStream(
            samplerate=48000, blocksize = self.blocksize, callback=callback_playback, channels=1)
        self.stream.start()
        self.queue_phase = 0

    def play(self, data):

        frequency = data["frequency"]
        amplitude = data["amplitude"]
        WAVEDATA = [amplitude * math.sin(2*math.pi*frequency*x/self.sample_rate + self.buffer_phase) for x in range(self.blocksize)]
        try:
            self.buffer.put_nowait(np.array(WAVEDATA, dtype=np.float32))
            self.buffer_phase = (2*math.pi*frequency*(self.blocksize-1)/self.sample_rate + self.buffer_phase) % (2*math.pi)
        except:
            pass
        
    def add_to_queue(self, data):
        duration = data["duration"]
        frequency = data["frequency"]
        amplitude = data["amplitude"]

        if(frequency is not None):
            for _ in range(int(duration*self.sample_rate/self.blocksize)):
                WAVEDATA = [amplitude * math.sin(2*math.pi*frequency*x/self.sample_rate + self.queue_phase) for x in range(self.blocksize)]
                self.queue.put_nowait(np.array(WAVEDATA, dtype=np.float32))
                self.queue_phase = (2*math.pi*frequency*(self.blocksize-1)/self.sample_rate + self.queue_phase) % (2*math.pi)
    
    def empty_queue(self, data):
        self.queue = queue.Queue()
        