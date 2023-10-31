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

        #self.processor = AutoProcessor.from_pretrained(model_name_or_path)
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name_or_path)
        #self.sampling_rate = self.feature_extractor.sampling_rate
        self.model = Wav2Vec2Model.from_pretrained(model_name_or_path).to(self.device)

        self.pipelineclassifier = pipeline("audio-classification", model=model_name_or_path)
        self.create_callback("predict", self.predict)

        #print(self.pipelineclassifier.config)

    def predict(self, data : dict):
        """
        data["activity_buffer"] : audio list
            -> float32
            
        
        """
        ## Outputs activity probablitily
        data = np.array(data['audio_buffer'])
        #data = self.feature_extractor(data)
        #data = {"inputs" : data, "attention_mask" : np.array([1 for i in range(len(data))])}
        

        #inputs = self.feature_extractor(data, sampling_rate = self.sampling_rate)
        
        #inputs = {key: torch.Tensor(inputs[key][0]) for key in inputs}
        #inputs = {"inputs" : data }

        #print(inputs.shape)

  
        with torch.no_grad():
            outputs = self.pipelineclassifier(data)


        #scores = F.softmax(logits, dim=1).detach().cpu().numpy()[0]

        #outputs = [{"Emotion": self.config.id2label[i], "Score": f"{round(score * 100, 3):.1f}%"} for i, score in enumerate(scores)]

        #Send it back to the application
        self.set_event_data(
            "speech_emotion",
            {
               "results": outputs,
            },
        )
        #return speech_prob


