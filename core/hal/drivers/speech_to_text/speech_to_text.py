from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
from core.hal.drivers.speech_to_text.fast_whisper.fast_whisper import WhisperModel
import time

class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        #create driver event
        self.register_to_driver("microphone", "audio_stream")
        self.register_to_driver("speech_activity_detection", "activity")

        self.create_event("transcription")

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.blocks = []

        self.model = WhisperModel("medium.en", device="cuda", compute_type="int8")

        
        #self.create_callback_on_event("transcription", self.transcript, "microphone", "audio_stream")

    def recording(self, data):
        block = data["block"][:, 0]        
  
        self.blocks.extend(block)
        print('extending')


    def transcribe(self, data):
        start = time.time()

        audio = data["block"][:, 0]
        segments = self.model.transcribe(audio, beam_size = 5)
        
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        
        print('durée : ', time.time() - start)
        self.blocks = []


    # def transcript(self, data):



    #     """Estimates the frequency of the input data"""

    #     block = data["block"][:, 0]
        
    #     # change the time needed depending on the Activity detection Module 
    #     if len(self.blocks) < 50*10*len(block):
            
    #         self.blocks.extend(block)
    #         print('extending')
    #     else:
    #         self.blocks = self.blocks[:50*10*len(block)]
            
    #         #self.blocks.extend(block)
    #         samplerate = data["samplerate"]
    #         # convert the sample rate 
            
        


    #         start = time.time()
    #         segments = self.model.transcribe(self.blocks, beam_size = 5)
            
    #         for segment in segments:
    #             print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

            
    #         print('durée : ', time.time() - start)
    #         self.blocks = []


        

        


        # self.set_event_data("frequency", {
        #     "max_frequency": freq[np.argmax(rfft)],
        #     "rfft": list(rfft[freq<self.MAX_FREQUENCY]),
        #     "amplitude": np.max(rfft),
        #     "blocksize": len(block),
        # })
