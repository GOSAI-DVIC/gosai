import os
import pickle
import sys
import threading
import time

import redis


class Console(threading.Thread):
    """A console to interract with the OS"""

    def __init__(self, hal, server, app_manager):
        threading.Thread.__init__(self)
        self.hal = hal
        self.server = server
        self.app_manager = app_manager
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        @self.server.sio.on("execute_command")
        def _(data) -> None:
            eval_command(self, data["command"])

    def run(self):
        time.sleep(1)
        print("")
        while 1:
            time.sleep(0.5)
            print("")
            command = input()
            eval_command(self, command)

    def log(self, content, level=2):
        """Logs via the redis database"""
        data = {"source": "console", "content": content, "level": level}
        self.db.set(f"log", pickle.dumps(data))
        self.db.publish(f"log", pickle.dumps(data))


def eval_command(console: Console, command: str) -> None:
    execute = command.split()[0]
    arguments = command.split()[1:]

    if execute == "exit":
        console.log("Exiting...")
        sys.exit()

    elif execute == "help":
        result = "Available commands:\n"
        result += "    exit - exit the application\n"
        result += "    help - show this help\n"
        result += "    ls drivers - list all available drivers\n"
        result += "    ls applications - list all available applications\n"
        result += "    log $level - set the log level\n"
        result += "    restart $app_name - restart an app\n"
        result += "    start $app_name - start an app\n"
        result += "    stop $app_name - stop an app\n"
        console.log(result)

    elif execute == "start":
        if len(arguments) == 0:
            console.log("Please specify an application to start", 3)
        else:
            console.app_manager.start(arguments[0])

    elif execute == "stop":
        if len(arguments) == 0:
            console.log("Please specify an application to stop", 3)
        else:
            console.app_manager.stop(arguments[0])

    elif execute == "restart":
        if len(arguments) == 0:
            console.log("Please specify an application to restart", 3)
        elif len(arguments) == 1:
            console.app_manager.stop(arguments[0])
            console.app_manager.start(arguments[0])

    elif execute == "ls":
        if len(arguments) == 1 and arguments[0] == "drivers":
            result = "Available drivers:\n"
            result += "\n".join(console.hal.get_drivers()) + "\n"
            console.log(result)

        if (
            len(arguments) == 2
            and arguments[0] == "drivers"
            and arguments[1] == "started"
        ):
            result = "Started drivers:\n"
            result += "\n".join(console.hal.get_started_drivers()) + "\n"
            console.log(result)

        if (
            len(arguments) == 2
            and arguments[0] == "drivers"
            and arguments[1] == "stopped"
        ):
            result = "Stopped drivers:\n"
            result += "\n".join(console.hal.get_stopped_drivers()) + "\n"
            console.log(result)

        if len(arguments) == 1 and arguments[0] == "applications":
            result = "Available applications:\n"
            result += "\n".join(console.app_manager.list_applications()) + "\n"
            console.log(result)

        if (
            len(arguments) == 2
            and arguments[0] == "applications"
            and arguments[1] == "started"
        ):
            result = "Started applications:\n"
            result += "\n".join(console.app_manager.list_started_applications()) + "\n"
            console.log(result)

        if (
            len(arguments) == 2
            and arguments[0] == "applications"
            and arguments[1] == "stopped"
        ):
            result = "Stopped applications:\n"
            result += "\n".join(console.app_manager.list_stopped_applications()) + "\n"
            console.log(result)

    elif execute == "log":
        if len(arguments) == 1:
            try:
                assert int(arguments[0]) in range(0, 3)
                os.environ["LOG_LEVEL"] = str(int(arguments[0]))
                console.log("Log level set to " + arguments[0], 3)
            except Exception as e:
                console.log("Invalid log level: " + str(e))
        else:
            console.log("Please specify a log level", 3)

    else:
        console.log("Unknown command: " + command, 3)
