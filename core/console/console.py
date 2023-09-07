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
        self.service = "core"
        self.name = "console"
        self.hal = hal
        self.server = server
        self.app_manager = app_manager
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        @self.server.sio.on(f"{self.service}-{self.name}-execute_command")
        def _(data) -> None:
            eval_command(self, data["command"])

    def run(self):
        time.sleep(1)
        while 1:
            time.sleep(0.5)
            print("")
            command = input()
            eval_command(self, command)

    def log(self, content, level=2):
        """Logs via the redis database"""
        data = {
            "service": "core",
            "source": "console",
            "content": content,
            "level": level,
        }
        self.db.set(f"log", pickle.dumps(data))
        self.db.publish(f"log", pickle.dumps(data))


def eval_command(console: Console, command: str) -> None:
    try:
        execute = command.split()[0]
        arguments = command.split()[1:]

        if execute == "applications":
            if len(arguments) == 0:
                helper(console, "applications")
                return

            if len(arguments) == 1 and arguments[0] == "ls":
                result = "\nAvailable applications:\n"
                result += (
                    "\n".join(
                        [
                            "\t" + app["name"]
                            for app in console.app_manager.list_applications()
                        ]
                    )
                    + "\n"
                )
                console.log(result)
                return

            if (
                len(arguments) == 2
                and arguments[0] == "ls"
                and arguments[1] == "started"
            ):
                result = "\nStarted applications:\n"
                result += (
                    "\n".join(
                        [
                            "\t" + app["name"]
                            for app in console.app_manager.list_started_applications()
                        ]
                    )
                    + "\n"
                )
                console.log(result)
                return

            if (
                len(arguments) == 2
                and arguments[0] == "ls"
                and arguments[1] == "stopped"
            ):
                result = "\nStopped applications:\n"
                result += (
                    "\n".join(
                        [
                            "\t" + app["name"]
                            for app in console.app_manager.list_stopped_applications()
                        ]
                    )
                    + "\n"
                )
                console.log(result)
                return

            if len(arguments) == 1 and arguments[0] == "start":
                console.log("Please specify an application to start", 3)
                return

            if len(arguments) == 1 and arguments[0] == "stop":
                console.log("Please specify an application to stop", 3)
                return

            if len(arguments) == 1 and arguments[0] == "restart":
                console.log("Please specify an application to restart", 3)
                return

            if len(arguments) == 2 and arguments[0] == "start":
                console.app_manager.start(arguments[1])
                return

            if len(arguments) == 2 and arguments[0] == "stop":
                console.app_manager.stop(arguments[1])
                return

            if len(arguments) == 2 and arguments[0] == "restart":
                console.app_manager.stop(arguments[1])
                console.app_manager.start(arguments[1])
                return

            helper(console, "applications")
            return

        elif execute == "drivers":
            if len(arguments) == 0:
                helper(console, "drivers")
                return

            if len(arguments) == 1 and arguments[0] == "ls":
                result = "\nAvailable drivers:\n"
                result += (
                    "\n".join(
                        ["\t" + driver["name"] for driver in console.hal.get_drivers()]
                    )
                    + "\n"
                )
                console.log(result)
                return

            if (
                len(arguments) == 2
                and arguments[0] == "ls"
                and arguments[1] == "started"
            ):
                result = "\nStarted drivers:\n"
                result += (
                    "\n".join(
                        [
                            "\t" + driver["name"]
                            for driver in console.hal.get_started_drivers()
                        ]
                    )
                    + "\n"
                )
                console.log(result)
                return

            if (
                len(arguments) == 2
                and arguments[0] == "ls"
                and arguments[1] == "stopped"
            ):
                result = "\nStopped drivers:\n"
                result += (
                    "\n".join(
                        [
                            "\t" + driver["name"]
                            for driver in console.hal.get_stopped_drivers()
                        ]
                    )
                    + "\n"
                )
                console.log(result)
                return

            if len(arguments) == 2 and arguments[0] == "get":
                console.log("You must specify the event name")
                return

            if len(arguments) == 3 and arguments[0] == "get":
                data = console.hal.get_driver_event_data(arguments[1], arguments[2])
                if data is False or data is None:
                    return
                result = f"The last data of {arguments[1]} on {arguments[2]} is {data}"
                console.log(result)
                return

            helper(console, "drivers")
            return

        elif execute == "exit":
            console.log("Exiting...")
            os.system('/bin/bash -c "make stop &> /dev/null"')

        elif execute == "help":
            if len(arguments) == 0:
                helper(console)
                return

            if len(arguments) == 1:
                helper(console, arguments[0])
                return

        elif execute == "log":
            if len(arguments) == 1:
                try:
                    assert int(arguments[0]) in range(0, 4)
                    os.environ["LOG_LEVEL"] = str(int(arguments[0]))
                    console.log("Log level set to " + arguments[0], 3)
                    return
                except Exception as e:
                    console.log("Invalid log level: " + str(e))
                    return
            else:
                console.log("Please specify a log level", 3)
                return

        elif execute == "password":
            if len(arguments) == 0:
                helper(console, "password")
                return

            if len(arguments) == 1 and arguments[0] == "show":
                result = (
                    "Password to access control: " + console.server.control_password
                )
                console.log(result)
                return

            elif len(arguments) == 1 and arguments[0] == "generate":
                console.server.generate_control_password()
                result = (
                    "New password to access control generated: "
                    + console.server.control_password
                )
                console.log(result)
                return

            helper(console, "password")
            return

        # elif execute == "reboot":
        #     console.log("Rebooting...")
        #     os.system('/bin/bash -c "make stop &> /dev/null" && make boot')

        console.log("Unknown command: " + command, 3)
    except Exception as e:
        console.log("Error: " + str(e), 3)


def helper(console: Console, exec_name: str = "") -> None:
    """Helper function to show the help"""
    if exec_name == "":
        result = "\nAvailable commands:\n"
        result += "\tapplications - show / manipulate applications\n"
        result += "\tdrivers      - show / manipulate drivers\n"
        # result += "\texit         - exit the program\n"
        result += "\thelp         - show this helper / the helper of a command\n"
        result += "\tlog          - show / manipulate the log level\n"
        result += "\tpassword     - show / generate a new password\n"
        result += "\n"
        result += "For more information about a command, type 'help <command>'\n"

        console.log(result)
        return

    elif exec_name == "applications":
        result = "\nName:\n"
        result += "\tapplications - show / manipulate applications\n\n"
        result += "Usage:\n"
        result += "\tapplications [arguments]\n\n"
        result += "Arguments:\n"
        result += "\tls - List all available applications\n"
        result += "\tls started - List all started applications\n"
        result += "\tls stopped - List all stopped applications\n"
        result += "\tstart <application_name> - Start an application\n"
        result += "\tstop <application_name> - Stop an application\n"
        result += "\trestart <application_name> - Restart an application\n"
        console.log(result)
        return

    elif exec_name == "drivers":
        result = "\nName:\n"
        result += "\tdrivers - show / manipulate drivers\n\n"
        result += "Usage:\n"
        result += "\tdrivers [arguments]\n\n"
        result += "Arguments:\n"
        result += "\tls - List all available drivers\n"
        result += "\tls started - List all started drivers\n"
        result += "\tls stopped - List all stopped drivers\n"
        result += "\tget <driver_name> <event_name> - Get the last data of an event\n"

        console.log(result)
        return

    elif exec_name == "log":
        result = "\nName:\n"
        result += "\tlog - show / manipulate the log level\n\n"
        result += "Usage:\n"
        result += "\tlog [arguments]\n\n"
        result += "Arguments:\n"
        result += "\t<log_level> - Set the log level\n"
        result += "\t\t1 - Debug\n"
        result += "\t\t2 - Info\n"
        result += "\t\t3 - Warning\n"
        console.log(result)
        return

    elif exec_name == "password":
        result = "\nName:\n"
        result += "\tpassword - show / generate a new password\n\n"
        result += "Usage:\n"
        result += "\tpassword [arguments]\n\n"
        result += "Arguments:\n"
        result += "\tshow - Show the current password\n"
        result += "\tgenerate - Generate a new password\n"
        console.log(result)
        return

    else:
        console.log("Unknown command: " + exec_name, 3)
        return
