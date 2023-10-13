from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
from core.hal.drivers.speech_to_text.fast_whisper.fast_whisper import WhisperModel
import time
import samplerate
import torch
# import webrtcvad

class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        #create driver event
        self.register_to_driver("microphone", "audio_stream")
        
        self.create_event("activity")

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.blocks = []

        self.patience = 0
        self.window = []
        # self.vad = webrtcvad.Vad(2)

        self.sr = 16000
        self.model, self.utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                    model='silero_vad',
                                    force_reload=True)



        
        #self.create_callback_on_event("activity", self.activity, "microphone", "audio_stream")



    def predict(self, audio_chunk : np.array):
        ## just probabilities

        speech_prob = self.model(audio_chunk, self.sr).item()

        return speech_prob

# wav = read_audio('en_example.wav', sampling_rate=SAMPLING_RATE)
# speech_probs = []
# window_size_samples = 1536
# for i in range(0, len(wav), window_size_samples):
#     chunk = wav[i: i+ window_size_samples]
#     if len(chunk) < window_size_samples:
#       break
#     speech_prob = model(chunk, SAMPLING_RATE).item()
#     speech_probs.append(speech_prob)
# vad_iterator.reset_states() # reset model states after each audio

# print(speech_probs[:10]) # first 10 chunks predicts
    def activity(self, data):
        """Estimates the frequency of the input data"""

        frame = data["block"][:, 0]
        # change the time needed depending on the Activity detection Module 
       
       
        
        #self.blocks.extend(block)
        sample_rate = data["samplerate"]
        # convert the sample rate 
        
        frame = samplerate.resample(frame, 16000 * 1.0 / 48000, 'sinc_best')  


        frame = np.int16(frame * 32768)

        print(len(frame))
        # get speech timestamps from full audio file
        #self.model(audio, 16000).item()
        pred = self.vad.is_speech(frame.tobytes(), 16000)
        
        self.window.append(pred)
        if len(self.window) <= 3 :
            self.window.append(pred)
        elif len(self.window) == 4 :
            if True in self.window :
                pred = True 

            self.window = self.window[1:]

        

        print('confidence : ', pred)
        self.set_event_data(
            "activity",
            {
                "confidence": pred,
            },
        )
        self.blocks = []


        

        


        # self.set_event_data("frequency", {
        #     "max_frequency": freq[np.argmax(rfft)],
        #     "rfft": list(rfft[freq<self.MAX_FREQUENCY]),
        #     "amplitude": np.max(rfft),
        #     "blocksize": len(block),
        # })
