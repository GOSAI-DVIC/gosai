from typing import Tuple
import numpy as np
import pyaudio
import time
import torch
from core.hal.drivers.driver import BaseDriver
from core.hal.drivers.voice_command.utils.cnn.inference import CNNInference
from core.hal.drivers.voice_command.utils.fuzzywuzzy.comparaison import Commands
from core.hal.drivers.voice_command.utils.tts.pytts import VocalFeedback
from queue import Queue
import whisper
import librosa
import sys


torch.cuda.empty_cache()

device = 'cpu'
#WHISPER model settings:
model = whisper.load_model("base.en")
LANGUAGE = "English"

#import GOSAI commands
GOSAIcommands = Commands()
#import Vocal feedbacks
VocalReturn = VocalFeedback()

#import WUW inference
WUWinf = CNNInference()

#Stream settings
CHANNEL=1
FORMAT=pyaudio.paFloat32
SAMPLE_RATE=44100
RUN=True
STTRun = False
#duration of wake up word audio (sec)
WUWSECONDS=2
#duration of speech to text audio (sec)
STTSECONDS=4


SLIDING_WINDOW=1/6
Numberofsttwindows = 3
CHUNK = int(SLIDING_WINDOW*SAMPLE_RATE*WUWSECONDS)  #equivalent to 20ms

WUWfeed_samples=SAMPLE_RATE*WUWSECONDS   
STTfeed_samples=SAMPLE_RATE*STTSECONDS

silence_threshold = 0.03

inference= CNNInference()


def get_audio_input_stream(callback)->pyaudio.PyAudio:
    stream = pyaudio.PyAudio().open(
        format=FORMAT,
        channels=CHANNEL,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK,
        # input_device_index=0,
        input_device_index=18,
        stream_callback=callback)
    return stream


data = np.zeros(WUWfeed_samples, dtype=np.float32) 

wuwq = Queue()
sttq = Queue()

def callback(in_data:np.array, frame_count, time_info, flag)->Tuple[np.array,pyaudio.PyAudio]:
    # print(9)
    global data, RUN, wuwq, sttq, STTRun      
    data0 = np.frombuffer(in_data, dtype=np.float32)
    data = np.append(data,data0)  
    # print(10)
    
    if STTRun == True:
        if len(data) > STTfeed_samples:
            data = data[-STTfeed_samples:]
            sttq.put(data)
            data = data[-STTfeed_samples//2:]

    else : 
        if len(data) > WUWfeed_samples:
            data = data[-WUWfeed_samples:]
            # print(11)
            # print(data)
            wuwq.put(data)
            print("Q-Size call back", wuwq.qsize())
            

    return (in_data, pyaudio.paContinue)

  
   
class Driver(BaseDriver):
    def __init__(self, name: str, parent, max_fps: int = 120) -> None:
        super().__init__(name, parent)

        self.command = None
        self.create_event("command")
        
        self.stream = get_audio_input_stream(callback)
        print("driver voice_command well initialised")

    def pre_run(self) -> None:
        super().pre_run()

    def loop(self) -> None:
        global RUN, STTRun
        print("1")
        time.sleep(3)
        print("Q-Size loop", wuwq.qsize())
        print("2")
        datarecup = wuwq.get()
        print("3")
        noiseValue = np.abs(datarecup).mean()
        print("noise value -> ",noiseValue)      
        if noiseValue>silence_threshold:       
            new_trigger = inference.get_prediction(torch.tensor(datarecup))
           
            if new_trigger==1:
                print('Wake Up Word triggered -> not activated')

            if new_trigger== 0:
                print("Wake Up Word triggered -> activated ")
                print(" ************ Speech To Text ************\nListening ...")
                STTRun = True               
                nbtranscription = 0              
                starttest = time.time()
                self.command = []
                while nbtranscription < 1 :
                    if not sttq.empty():                       
                        STTdatarecup = sttq.get() 
                        STTdatarecup = librosa.resample(STTdatarecup, orig_sr = 44100, target_sr=16000)         
                        if len(STTdatarecup) >= STTSECONDS*16000: 
                                result = model.transcribe(STTdatarecup, language=LANGUAGE)
                                STTresult = result["text"]
                                print("transcription : ",STTresult)
                                GOSAIcommands.comparaison(STTresult)
                                if GOSAIcommands.modeactive != None :
                                    print("mode active : ",GOSAIcommands.modeactive)
                                    self.command.append(GOSAIcommands.modeactive)                                   
                                    GOSAIcommands.modeactive = None
                                nbtranscription += 1

                   
                    STTRun = False
                    if len(self.command) > 0:
                        for k in self.command:
                            if k[0]=='start':
                                VocalReturn.speak(k[1],'started')

                            if k[0]=='stop':
                                VocalReturn.speak(k[1],'stopped')
                    print("time STT: ",time.time()-starttest)
                    self.set_event_data("command", self.command)                 
                    print(" ************ End of Speech To Text ************\n")