from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):

    def __init__(self, name: str, parent, fps: int = 30):
        super().__init__(name, parent)
        self.fps = fps

        #create driver event
        self.create_event("audio_recorded")

    def pre_run(self):
        # runs to do at the start of the driver
        pass

    def listen(self):
        pass

    def save_audio(self):
        pass

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
