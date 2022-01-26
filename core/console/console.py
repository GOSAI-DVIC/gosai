import os
import threading
import time

class Console(threading.Thread):
    """ A console to interract with the OS """
    def __init__(self, hal, server, app_manager):
        threading.Thread.__init__(self)
        self.hal = hal
        self.server = server
        self.app_manager = app_manager

    def run(self):
        time.sleep(1)
        print("")
        while 1:
            print("")
            command = input(">>: ")
            execute = command.split()[0]
            arguments = command.split()[1:]

            if execute == "exit":
                exit()
            elif execute == "help":
                print("Available commands:")
                print("exit - exit the application")
                print("help - show this help")
                print("ls - list all available drivers")
                print("log $level - set the log level")
                print("restart - restart an app")
                print("start $app_name - start an app")
                print("stop $app_name - stop an app")
                #print("status - show the status of an app")
                print("ps - displays informations of the drivers")

            elif execute == "start":
                if len(arguments) == 0:
                    print("Please specify an application to start")
                else:
                    self.app_manager.start(arguments[0])

            elif execute == "stop":
                if len(arguments) == 0:
                    print("Please specify an application to stop")
                else:
                    self.app_manager.stop(arguments[0])

            elif execute == "restart":
                if len(arguments) == 0:
                    print("Please specify an application to restart")
                elif len(arguments) == 1:
                    self.app_manager.stop(arguments[0])
                    self.app_manager.start(arguments[0])

            elif execute == "exit":
                exit()

            elif execute == "ls":
                if len(arguments) == 1 and arguments[0] == "drivers":
                    print("Available drivers:")
                    print("\n".join(self.hal.get_drivers()))

                if len(arguments) == 2 and arguments[0] == "drivers" and arguments[1] == "started":
                    print("Started drivers:")
                    print("\n".join(self.hal.get_started_drivers()))

                if len(arguments) == 2 and arguments[0] == "drivers" and arguments[1] == "stopped":
                    print("Stopped drivers:")
                    print("\n".join(self.hal.get_stopped_drivers()))

                if len(arguments) == 1 and arguments[0] == "applications":
                    print("Available applications:")
                    print("\n".join(self.app_manager.list_applications()))

                if len(arguments) == 2 and arguments[0] == "applications" and arguments[1] == "started":
                    print("Started applications:")
                    print("\n".join(self.app_manager.list_started_applications()))

                if len(arguments) == 2 and arguments[0] == "applications" and arguments[1] == "stopped":
                    print("Stopped applications:")
                    print("\n".join(self.app_manager.list_stopped_applications()))

            elif execute == "log":
                if len(arguments) == 1:
                    try:
                        os.environ["LOG_LEVEL"] = str(int(arguments[0]))
                    except:
                        print("Invalid log level")
                else:
                    print("Please specify a log level")

            else:
                print("Unknown command")
