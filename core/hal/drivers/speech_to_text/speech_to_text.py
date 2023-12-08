from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
import os 
import time
from faster_whisper import WhisperModel

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch


class Driver(BaseDriver):

    def __init__(self, name: str, parent, model : bool = 'faster_whisper'):
        super().__init__(name, parent)
        self.create_event('transcription')
        self.model_str = model 

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.debug = True
        self.fast_whisper_bool = False
        self.path_dir = 'core/hal/drivers/speech_to_text/models'
        self.model_size = 'medium.en'

        if self.model_str == 'faster_whisper' :
           
            self.pipe = WhisperModel(model_size_or_path = '/home/hugo/Desktop/Project/gosai/core/hal/drivers/speech_to_text/models/models--Systran--faster-whisper-medium.en/snapshots/a29b04bd15381511a9af671baec01072039215e3', device="cuda", compute_type="int8")
            
        else : 


            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.log(self.device, 3)
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            model_id = "distil-whisper/distil-medium.en"
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
            )
            processor = AutoProcessor.from_pretrained(model_id)
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                max_new_tokens=128,
                torch_dtype=torch_dtype,
                device=self.device,
            )
        #self.model = WhisperModel("medium.en", device="cuda", compute_type="int8")
        self.create_callback("transcribe", self.transcribe)


    def transcribe(self, data : dict):
        """
        data["audio_buffer"] : audio list
            -> float32
            -> 16000Hz
        """
        start = time.time()
        audio = data["audio_buffer"]

      
            #Save last audio buffer to file for debugging 
           
       # self.log("transcription",3)

        if self.model_str=='faster_whisper' :
            segments, info = self.pipe.transcribe(np.array(audio), beam_size = 5)
            txt = ''
            for segment in segments : 
                txt = txt + segment.text 


        else :
            with torch.cuda.device(self.device):
                txt = self.pipe(np.array(audio))['text']

        #self.log("self.model.transcribe",3)     
        # for segment in segments:
        #     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        self.set_event_data(
            "transcription",
            {
                "transcription_segments": txt,
                "audio_duration": len(audio)/16000,
                "transcription_duration": time.time() - start,
            },
        )
        #self.log("finished printing segments",3)

   

def save_audio(audio):
    audio_int16 = np.int16(audio/np.max(np.abs(audio)) * 32767)
    write('test.wav', 16000, audio_int16)


