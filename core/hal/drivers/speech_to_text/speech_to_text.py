from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
from core.hal.drivers.speech_to_text.fast_whisper.fast_whisper import WhisperModel
import time

from scipy.io.wavfile import write




import gc
import io
import itertools

from typing import BinaryIO, Union

import av



#core.hal.drivers.speech_to_text.fast_whisper.
class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        #create driver event
        # self.register_to_driver("microphone", "audio_stream")
        # self.register_to_driver("speech_activity_detection", "activity")

        self.create_event('transcription')
        

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.blocks = []

        self.model = WhisperModel("medium.en", device="cuda", compute_type="int8")

        self.create_callback("transcribe", self.transcribe)


    def transcribe(self, data):
        start = time.time()

        audio = data["full_audio"]

        save_audio(audio)

        print(len(audio))
        print(f'duration audio is {len(audio)/16000}s')

        self.log("transcription",3)
        segments = self.model.transcribe(audio, beam_size = 5)
        
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

  
        print('durée : ', time.time() - start)
   

def save_audio(audio):
    audio_int16 = np.int16(audio/np.max(np.abs(audio)) * 32767)
    write('test.wav', 16000, audio_int16)


# if __name__ == '__main__' :

#     model = WhisperModel("medium.en", device="cuda", compute_type="int8")