import logging
import os
import sys
import time
from queue import Queue

from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# import eventlet
# import socketio

# logging.getLogger("socketio").setLevel(logging.ERROR)
# logging.getLogger("engineio").setLevel(logging.ERROR)
# logging.getLogger("eventlet").setLevel(logging.ERROR)

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO


class quietServer(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_chrome():
    def _start_chrome():
        options = ["--start-fullscreen", "--incognito", "--disable-logging"]
        options_line = " ".join(options)
        cmd = f"chromium http://127.0.0.1:8000/core/display {options_line}"
        os.system(f'/bin/bash -c "{cmd} &> /dev/null"')

    threading.Thread(target=_start_chrome, args=(), daemon=True).start()


class Server:
    def __init__(self, hal):
        # self.sio = socketio.Server(
        #     logger=True,
        #     cors_allowed_origins="*"
        # )  # Creates the socketio server

        # self.app = socketio.WSGIApp(self.sio)

        self.app = Flask(__name__)
        self.sio = SocketIO(
            self.app,
            logger=False,
            engineio_logger=False,
            async_mode="eventlet",
            cors_allowed_origins="*",
        )

        self.hal = hal

        self.queue = Queue()
        # self.started = False

        @self.sio.on("connect")
        def connect(*args):
            # self.hal.log("server: Client connected")
            self.sio.start_background_task(self.send_queued_data)

    def start(self, socket_port=5000, server_port=8000):
        """Starts the server on the given port"""

        def _start_socket(self, port):

            # eventlet.wsgi.server(eventlet.listen(("", port)), self.app, log_output=True)

            self.sio.run(self.app, host="0.0.0.0", port=port)

        def _start_server(self, port):
            server_address = ("0.0.0.0", port)
            self.httpd = HTTPServer(server_address, quietServer)
            self.httpd.serve_forever()

        threading.Thread(
            target=_start_server, args=(self, server_port), daemon=True
        ).start()
        threading.Thread(
            target=_start_socket, args=(self, socket_port), daemon=True
        ).start()

    def respond(self, name, data):
        """
        Directly respond to a client event
        To be placed in a socketio.on()
        """

        self.sio.emit(name, data)

    def send_data(self, name, data):
        """Send data to all connected clients"""

        self.queue.put((name, data))

    def send_queued_data(self):
        """Send queued data to all connected clients"""

        while True:
            self.sio.sleep(0.0001)
            if not self.queue.empty():
                name, data = self.queue.get()
                self.sio.emit(name, data)
            # if self.data != ():
            #     name, data = self.data
