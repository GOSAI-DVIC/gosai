import speech_recognition as sr
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):

    def __init__(self, name: str, parent, fps: int = 30):
        super().__init__(name, parent)
        self.fps = fps

        self.recognizer = sr.Recognizer()

        print('-'*40)
        self.source = sr.Microphone()
        print('-'*40)
        print('Don\'t consider the output from ALSA lib to JackShm : there are just informatives')
        print('-'*40, end='\n\n')

        #create driver event
        self.create_event("audio_recorded")

    def pre_run(self):
        # runs to do at the start of the driver
        pass

    def listen(self):
        print("Speak : ")
        self.recognizer.adjust_for_ambient_noise(self.source)
        return self.recognizer.listen(self.source)

    def save_audio(self):
        print("Speak : ")
        self.recognizer.adjust_for_ambient_noise(self.source)
        audio = self.recognizer.listen(self.source)
        with open("audio_file.wav", "wb") as file:
            file.write(audio.get_wav_data())

    # def loop(self):
    #     start_t = time.time()

    #     # update event
    #     # driver_event_1 = an_update_function_1()
    #     # driver_event_2 = an_update_function_2()

    #     #set module event
    #     # if driver_event_1 is not None:
    #         # self.set_event_data("driver_event_1", driver_event_1)
    #     # if driver_event_2 is not None:
    #         # self.set_event_data("driver_event_2", driver_event_2)

    #     time.sleep(1 / self.fps) #to temporize
