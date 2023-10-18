from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
from core.hal.drivers.speech_to_text.fast_whisper.fast_whisper import WhisperModel
import time

import io 
import av
from typing import BinaryIO, List, NamedTuple, Optional, Tuple, Union, Iterable
import itertools
import gc

from scipy.io.wavfile import write



#core.hal.drivers.speech_to_text.fast_whisper.
class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)
        self.create_event('transcription')
        

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.debug = True
        self.model = WhisperModel("medium.en", device="cuda", compute_type="int8")
        self.create_callback("transcribe", self.transcribe)


    def transcribe(self, data : dict):
        """
        data["audio_buffer"] : audio list
            -> float32
            -> 16000Hz
        """
        start = time.time()
        audio = data["audio_buffer"]

        if self.debug :
            #Save last audio buffer to file for debugging 
            save_audio(audio)
       # self.log("transcription",3)

        segments = self.model.transcribe(np.array(audio), beam_size = 5)

        #self.log("self.model.transcribe",3)     
        # for segment in segments:
        #     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        self.set_event_data(
            "transcription",
            {
                "transcription_segments": [segment for segment in segments],
                "audio_duration": len(audio)/16000,
                "transcription_duration": time.time() - start,
            },
        )
        #self.log("finished printing segments",3)

   

def save_audio(audio):
    audio_int16 = np.int16(audio/np.max(np.abs(audio)) * 32767)
    write('test.wav', 16000, audio_int16)


