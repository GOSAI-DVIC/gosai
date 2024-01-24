from core.hal.drivers.driver import BaseDriver
import torch
from TTS.api import TTS
import os

class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.type = "no_loop" # no loop driver
        #create driver event
        self.create_event("generate_audio")
        


    def pre_run(self):
        # runs to do at the start of the driver
        super().pre_run()
        # load tts model
        self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to("cuda")

        self.create_callback("run", self.generate_audio)

    def generate_audio(self, data):
        """
        Generate audio from text with a speaker id
        entry: dict["prompt": str, "speaker" str]
        return audio: np.array
        """
        audio = self.tts.tts_with_vc(
                    data["prompt"],
                    speaker_wav= os.path.join("core", "hal", "drivers", "tts", "speakers",data["speaker"])
                )
        self.set_event_data("generate_audio", audio)