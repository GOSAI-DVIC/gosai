import datetime
import locale
import os
import pickle
import threading

import redis

LOGS_PATH = "core/logs"
locale.setlocale(locale.LC_ALL, "")


class Logger:
    """
    Logger class
    """

    def __init__(self, server):
        """
        Constructor and API for the logger
        """
        self.server = server
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        self.history = []

        @self.server.sio.on("get_log_history")
        def _():
            self.server.send_data("log_history", {
                "history": self.history
            })

    def log(self, source, content, level=1):
        """
        Logs a message
        """

        log = {
            "time": datetime.datetime.now().strftime('%b-%d-%G-%I:%M:%S%p'),
            "source": source,
            "content": content,
            "level": level
        }
        if level >= int(os.environ["LOG_LEVEL"]):
            print(f"{log['level']} : {log['source']} : {log['content']}")
            self.history.append(log)
            self.server.send_data("log", log)

        if level >= 2:
            with open(f"{LOGS_PATH}/{source}.log", "a+") as log_file:
                log_file.write(
                    f"{log['level']} : {log['time']} : {log['content']}\n"
                )

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
                    self.log(data["source"], data["content"], data["level"])
                except pickle.UnpicklingError as e:
                    pass
                except Exception as e:
                    self.log("logger", f"Error while loading logged data: {e}", 3)
                    pass

        threading.Thread(target=_log_listenner, args=(self,)).start()

    def log_to_string(self, log):
        """
        Transforms a log to a string
        """
        return f"{log['source']}: {log['content']}"
