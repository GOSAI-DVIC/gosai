import datetime
import os
import pickle
import threading

import redis

LOGS_PATH = "core/logs"

class Logger:
    """
    Logger class
    """

    def __init__(self, server):
        """
        Constructor and API for the logger
        """
        self.service = "core"
        self.name = "logger"
        self.server = server
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        self.history = []

        @self.server.sio.on(f"{self.service}-{self.name}-get_log_history")
        def _():
            self.server.send_data(f"{self.service}-{self.name}-log_history", {"history": self.history})

        self.log_colors = {1: "\033[0m", 2: "\033[36m", 3: "\033[33m", 4: "\033[31m"}

    def log(self, service, source, content, level=1):
        """
        Logs a message. The message is displayed in the console,
        added to the history and sent to the clients.

        Parameters
        ----------
        service : str
            The service that logs the message (e.g. core, application, ...)

        source : str
            The source of the message (e.g. app_manager, console, ...)

        content : str
            The content of the message, describing what happened

        level : int
            The level of the message (1: info, 2: debug, 3: warning, 4: error)
        """
        log = {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "service": service,
            "source": source,
            "content": content,
            "level": level,
        }
        if level >= int(os.environ["LOG_LEVEL"]):
            print(self.log_to_string(log))
            self.history.append(log)
            self.server.send_data(f"{self.service}-{self.name}-log", log)

        if level >= 2:
            with open(f"{LOGS_PATH}/{source}.log", "a+") as log_file:
                log_file.write(f"{log['level']} : {log['time']} : {log['content']}\n")

    def log_listenner(self):
        """
        Listens for logs comming from the redis server
        """

        def _log_listenner(self):
            ps = self.db.pubsub()
            ps.subscribe("log")
            for binary_data in ps.listen():
                try:
                    data = pickle.loads(bytes(binary_data["data"]))
                    self.log(
                        data["service"], data["source"], data["content"], data["level"]
                    )
                except pickle.UnpicklingError:
                    pass
                except Exception as e:
                    self.log(
                        "core", "logger", f"Error while loading logged data: {e}", 3
                    )

        threading.Thread(target=_log_listenner, args=(self,)).start()

    def log_to_string(self, log):
        """
        Transforms a log to a string

        Parameters
        ----------

        log : dict
            The log to transform, should be a dict with the following keys:
            - time: the time of the log
            - service: the service that logs the message
            - source: the source of the message
            - content: the content of the message
            - level: the level of the message
        """
        # Fill the log with spaces to make it look nice
        return (
            f"{self.log_colors[log['level']]}{log['time']} : "
            + f"{log['level']} : {log['service'].ljust(12)} : "
            + f"{log['source'].ljust(15)}\033[0m : {log['content']}"
        )
