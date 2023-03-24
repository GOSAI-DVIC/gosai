


import torch
import torchaudio.transforms as T
import torchaudio.functional as F
import time

#from dataset import WakeWordDataset
from core.hal.drivers.voice_commands.utils.wakeupword.model.model import LSTM
from typing import Tuple
from sonopy import  mfcc_spec
import torch.nn as nn

class MFCC(nn.Module):

    def __init__(self, sample_rate, fft_size=400, window_stride=(400, 200), num_filt=40, num_coeffs=40):
        super(MFCC, self).__init__()
        self.sample_rate = sample_rate
        self.window_stride = window_stride
        self.fft_size = fft_size
        self.num_filt = num_filt
        self.num_coeffs = num_coeffs
        self.mfcc = lambda x: mfcc_spec(
            x, self.sample_rate, self.window_stride,
            self.fft_size, self.num_filt, self.num_coeffs
        )
    
    def forward(self, x):
        return torch.Tensor(self.mfcc(x.squeeze(0).cpu().numpy())).transpose(0, 1).unsqueeze(0)



def get_featurizer(sample_rate):
    return MFCC(sample_rate=sample_rate)



@torch.no_grad()
def predict(model, input:torch.Tensor, class_mapping:Tuple[int])->int:
    model.eval()
    prob = model(input)
    prediction = int(prob>0.1)
    return prediction,prob

class LSTMInference:
    def __init__(self,device, class_mapping:Tuple[int]=[0, 1]) -> None:
        self.model_lstm = LSTM(device).to(device)
        self.state_dict = torch.load("/home/hugo/Bureau/PythonProject/GOSAI/gosai/core/hal/drivers/voice_commands/utils/wakeupword/model/state_dict_model.pt",map_location=torch.device(device))
        self.model_lstm.load_state_dict(self.state_dict)
        self.class_mapping=class_mapping

        self.mfcc_transform = MFCC(sample_rate=16000).to(device)
       
    

    def get_prediction(self,x:torch.Tensor)->int:

        
        
       
        x= F.resample(x, 44100, 16000)
     
        mfcc = self.mfcc_transform(x)
        

        mfcc = mfcc.transpose(0,1).transpose(0,2)
       
        # if x.shape[1] > 16000:
        #     x = x[:, :16000]
        # elif x.shape[1] < 16000:
        #     num_missing_samples = 16000-x.shape[1]
        #     last_dim_padding = (0, num_missing_samples)
        #     x = torch.nn.functional.pad(x, last_dim_padding)
       
    
        prediction,prob =predict(self.model_lstm,mfcc.to("cuda"),self.class_mapping)

        
        return prediction,prob


