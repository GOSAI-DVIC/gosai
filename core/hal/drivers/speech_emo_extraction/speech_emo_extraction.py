from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
import numpy as np 
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model, pipeline, AutoConfig, AutoProcessor, AutoModel
import torch
import torch.nn.functional as F
# import webrtcvad

class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)
        self.create_event("speech_emotion")

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()
        self.device = 'cpu'
        self.debug = False
        model_name_or_path = "antonjaragon/emotions_xls53_6_classes"

        
        self.config = AutoConfig.from_pretrained(model_name_or_path)

   
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name_or_path)

        self.model = Wav2Vec2Model.from_pretrained(model_name_or_path).to(self.device)

        self.pipelineclassifier = pipeline("audio-classification", model=model_name_or_path)
        self.create_callback("predict", self.predict)

   

    def predict(self, data : dict):
        """
        data["activity_buffer"] : audio list
            -> float32
            
        """
      
        data = np.array(data['audio_buffer'])

  
        with torch.no_grad():
            outputs = self.pipelineclassifier(data)


        self.set_event_data(
            "speech_emotion",
            {
               "results": outputs,
            },
        )
        """
        outputs is a dict with all emotions associated with their scores
        avalaible emotions for the actual model : [Angry, Sad, Fearful, Happy, Disgusted, Neutral]
        """


