import pyttsx3


class VocalFeedback():
    
    def __init__(self):
        
        self.feedbacks = dict()
        with open("command.txt",'r') as f:
            lines = f.readlines()
            for line in lines :
                self.feedbacks[line.split("/")[1]] = line.split("/")[2]

    def speak(self, mode, trigger):
        engine = pyttsx3.init()
        engine.say(self.feedbacks[mode]+" "+trigger)
        engine.runAndWait()
        
