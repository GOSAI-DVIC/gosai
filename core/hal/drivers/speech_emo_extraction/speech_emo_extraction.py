from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
import numpy as np 
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSpeechClassification, AutoConfig
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
        model_name_or_path = 'ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition'
        self.config = AutoConfig.from_pretrained(model_name_or_path)
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name_or_path)
        self.sampling_rate = self.feature_extractor.sampling_rate
        self.model = Wav2Vec2ForSpeechClassification.from_pretrained(model_name_or_path).to(device)
        self.create_callback("predict", self.predict)


    def predict(self, data : dict):
        """
        data["activity_buffer"] : audio list
            -> float32
            -> 16000Hz
        
        """
        ## Outputs activity probablitily
        inputs = self.feature_extractor(data, sampling_rate = self.sampling_rate)
        inputs = {key: inputs[key].to(self.device) for key in inputs}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        scores = F.softmax(logits, dim=1).detach().cpu().numpy()[0]
        outputs = [{"Emotion": self.config.id2label[i], "Score": f"{round(score * 100, 3):.1f}%"} for i, score in enumerate(scores)]
        #Send it back to the application
        self.set_event_data(
            "speech_emotion",
            {
                "results": outputs,
            },
        )
        #return speech_prob


