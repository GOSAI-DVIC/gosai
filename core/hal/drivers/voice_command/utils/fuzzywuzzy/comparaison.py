from fuzzywuzzy import fuzz
import time


class Commands():
    def __init__(self):
        self.commandsdic = dict()
        with open("core/hal/drivers/voice_command/utils/command.txt",'r') as f:
            lines = f.readlines()
            for line in lines :
                self.commandsdic[line.split("/")[0]] = line.split("/")[1]
        self.modeactive = None 

    def comparaison(self, transcription : str):
        
        activefunc = False
        for command, activ in self.commandsdic.items():
            # t = time.time()


            start = fuzz.partial_token_set_ratio(transcription, "start")
            print("start prob : ", start)
            stop = fuzz.partial_token_set_ratio(transcription, "stop")
            print("stop prob : ", stop)
            # print("active prob : ", activation)
            if (start > 80 or stop > 80):
                if start > stop :
                    trigger = "start"
                else :
                    trigger = "stop"

                if activefunc == False :
                    print("active fonction recognized") 
                    activefunc = True
                
                #sim = fuzz.token_set_ratio(transcription, command)
                sim2 =     fuzz.partial_token_set_ratio(transcription, command)
                #print("token set ratio : ",sim)
                
                # print("checking for ", activ)
                # print("mode prob : ", sim2)

                if (sim2 > 85):
                    print("activation of : ", activ)
                    self.modeactive=[trigger,activ] 

            # end = time.time()
            # print("process time : ",end - t )
            # print("---------------------------------------------")



if __name__ == '__main__':
    GOSAIcommands = Commands()
    test = "Hello everyone"
    test2 = "triangle active"
    test3 = "activation of the triangles please GOSAI"
    test4 = "Hello everyone activation of the triangle please"
    test5 = "The life of activation of the triangle ok"
    GOSAIcommands.comparaison(test)
    GOSAIcommands.comparaison(test2)
    GOSAIcommands.comparaison(test3)
    GOSAIcommands.comparaison(test4)
    GOSAIcommands.comparaison(test5)
