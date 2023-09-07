# Hand Pose estimation Driver

import time

import numpy as np


from core.hal.drivers.driver import BaseDriver
from core.hal.drivers.voice_commands.utils.wakeupword.wakeupword_detection import LSTMInference
from core.hal.drivers.voice_commands.utils.voice_recognition import SpeechToText
from core.hal.drivers.voice_commands.utils.comparaison.comparaison import GOSAIcommands
from torch import Tensor as T 
from librosa import resample as rs
import socketio


class Driver(BaseDriver):
    """Hand pose driver"""
    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)

        self.register_to_driver("web_audio_stream", "web_audio_1sec")

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps
        self.window = 1
        #self.register_to_driver("VoiceCommands", "transcript")

    def pre_run(self):
        """Runs once at the start of the driver"""
        self.device = "cpu"
        self.WakeUpWord = LSTMInference(device=self.device)
        self.SpeechToText_model = SpeechToText.init()
        self.audio_buffer = np.zeros(0, dtype=np.float32)
        self.autocalibration = True
        self.SpeechToTextMode = False 
        self.SpeechToTextCount = 0
        self.sample_rate = 44100
        self.sio.connect('http://0.0.0.0:8000')
        self.Commands = GOSAIcommands()
        self.sio = socketio.Client()


    def loop(self):
        """Main loop"""
        start_t = time.time()

        audio = self.parent.get_driver_event_data("web_audio_stream", "web_audio_1sec")

        if audio is not None and (sum(audio)!=0):
            self.audio_buffer = np.append(self.audio_buffer, audio)
            #flag_1 = time.time()

            if self.audio_buffer == 88200 and not self.SpeechToTextMode: 
                noiseValue = np.abs(self.audio_buffer).mean()

                if self.autocalibration==True:
                    silence_treshold = noiseValue + 0.2*noiseValue
                    print("silence_treshold : ",silence_treshold)
                    self.autocalibration=False

                if noiseValue > silence_treshold:
                    print("noiseValue ------> ",noiseValue ,"   Wake Up Word triggered :")
                    #wavf.write("audio"+str(count)+".wav", 44100, wuwdata)
                    new_trigger, prob = self.WakeUpWord.get_prediction(self.device,T(wuwdata).to(self.device))

                    if new_trigger==1:

                        print('Not activated -------> ',prob)
                        
                    if new_trigger== 0:

                        self.SpeechToTextMode = True
                        self.SpeechToTextCount += 1

                        if self.SpeechToTextCount >= 4 :


                            STTint16 = rs(self.audio_buffer, orig_sr = 44100, target_sr=16000)

                            transcription = self.SpeechToText_model.transcribe(STTint16)
                            self.set_event_data("transcript", transcription)

                            print("transcription : ",transcription)

                            self.Commands.comparaison(transcription)

                            
                            #send to socketio to start the app
                            
                            self.sio.emit("core-app_manager-start_application", {
                            "application_name": self.Commands.modeactive[0]})

          


            #                 "core-app_manager-start_application", {
            #     application_name: app_name,
            # })

                            self.Commands.modeactive = []
                            #wavf.write("audio"+str(count)+".wav", 44100, wuwdata)
                            wuwdata = np.zeros(0, dtype=np.float32)
                            self.SpeechToTextCount = 0
                            self.SpeechToTextMode = False
                else :
                    print("silence    (",noiseValue,")")

            wuwdata = wuwdata[-self.samplerate:]

               




            
    

        # if self.debug_time:
        #     self.log(f"Total time: {(end_t - start_t)*1000}ms")
        #     self.log(f"FPS: {int(1/(end_t - start_t))}")

        # dt = max((1 / self.fps) - (end_t - start_t), 0.0001)
        # time.sleep(dt)
