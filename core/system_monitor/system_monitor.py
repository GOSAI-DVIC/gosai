# record : {"source": {"name": str, "type": str}, "type": str, "data": Any }


import datetime
import locale
import os
import pickle
import threading
import time

import redis

locale.setlocale(locale.LC_ALL, "")

class Monitor:
    """
    System monitor class
    """

    def __init__(self, server):
        """
        Constructor and API for the system monitor
        """
        self.service = "core"
        self.name = "system_monitor"
        self.server = server
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        self.recent_performances = {}
        self.display_stats = {}

        @self.server.sio.on(f"{self.service}-{self.name}-get_recent_performances")
        def _():
            self.server.send_data(f"{self.service}-{self.name}-recent_performances", {
                "performances": self.recent_performances
            })

        @self.server.sio.on(f"{self.service}-{self.name}-purge_recent_performances")
        def _():
            self.recent_performances = {}

        @self.server.sio.on(f"{self.service}-{self.name}-set_display_statistics")
        def set_display_statistics(data):
            self.display_stats = data
            self.server.sio.emit(f"{self.service}-{self.name}-display_statistics", data)

        @self.server.sio.on(f"{self.service}-{self.name}-get_display_statistics")
        def get_display_statistics():
            self.server.sio.emit(f"{self.service}-{self.name}-display_statistics", self.display_stats)



    def record_listenner(self):
        """
        Listens for performance records comming from the redis server
        """

        def _record_listenner(self):
            ps = self.db.pubsub()
            ps.subscribe("performance_record")
            for binary_data in ps.listen():
                try:
                    data = pickle.loads(bytes(binary_data["data"]))
                    rec_src_name = data["source"]["name"]
                    rec_src_type = data["source"]["type"]
                    rec_type = data["type"]
                    rec_data = data["data"]

                    if rec_src_type not in self.recent_performances:
                        self.recent_performances[rec_src_type] = {}
                    if rec_src_name not in self.recent_performances[rec_src_type]:
                        self.recent_performances[rec_src_type][rec_src_name] = {}
                    self.recent_performances[rec_src_type][rec_src_name][rec_type] = rec_data

                except pickle.UnpicklingError as e:
                    pass
                except Exception as e:
                    self.log(f"Error while loading performance data: {e}", 3)
                    pass


        thread = threading.Thread(target=_record_listenner, args=(self,))
        thread.start()


    def log(self, content, level=1):
        """Logs via the redis database"""
        data = {
            "service": "core",
            "source": self.name,
            "content": content,
            "level": level
        }
        self.db.set("log", pickle.dumps(data))
        self.db.publish("log", pickle.dumps(data))
