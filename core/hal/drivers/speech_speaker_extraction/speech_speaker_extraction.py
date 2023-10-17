from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
import time
import numpy as np 
import samplerate
from modelscope.models import Model
import torch


# if __name__ == '__main__':
#     model = Model.from_pretrained('damo/speech_campplus_sv_en_voxceleb_16k', device='cuda')
class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.create_event('speaker_emb')
        
    

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()
        
        self.ref_embeddings = {}
        self.treshold = 0.5
        
        self.model = Model.from_pretrained('damo/speech_campplus_sv_en_voxceleb_16k', device='cpu')
        self.create_callback("get_embedding", self.get_embedding)
        self.create_callback("speaker_verification", self.speaker_verification)

    def cosine_similarity(self, A, B):
        
        sim = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
        return sim(A,B)
                            
    def get_embedding(self, data):
        return self.model(data)
    
    def speaker_verification(self, data):

        results = {}

        embed = self.get_embedding(np.array(data["full_audio"]))
        if not data['new_user']:
            
            for spk, ref_emb in self.ref_embeddings.items() :
                sim = self.cosine_similarity(embed, ref_emb)
                if sim > self.treshold :
                    results[spk] = [True, sim]
                else : 
                    results[spk] = [False, sim]
        
            
            self.set_event_data(
                "speaker_emb",
                {   
                    "embedding": embed,
                    "comparaison":results
                },
            )
        else :
            
            self.ref_embeddings[data["speaker_name"]] = embed
            print('\n')
            self.log("User added succesfully", 3)
            print('\n')

        return results 
