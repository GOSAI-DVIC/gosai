from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
from core.hal.drivers.speech_to_text.fast_whisper.fast_whisper import WhisperModel
import time
import numpy as np 
import samplerate
from modelscope.models import Model


class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        #create driver event
        self.register_to_driver("microphone", "audio_stream")
        

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()
        
        self.ref_embeddings = {}
        self.treshold = 0.5
        self.model = Model.from_pretrained('damo/speech_campplus_sv_en_voxceleb_16k', device='cpu')

    
    def cosine_similarity(self, A, B):
        return np.dot(A,B)/(np.linalgnorm(A)*np.linalgnorm(B))
                            
    def get_embedding(self, data):
        return self.model(data)
    
    def speaker_verification(self, data):

        results = {}
        embed = self.get_embedding(data)

        for spk, ref_emb in self.ref_embeddings.items() :
            sim = self.cosine_similarity(embed, self.reference_embed)
            if sim > self.treshold :
                results[spk] = [True, sim]
            else : 
                results[spk] = [False, sim]
        
        return results 


      