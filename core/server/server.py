import os
import threading
from queue import Queue

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO


def start_chrome():
    def _start_chrome():
        options = ["--start-fullscreen", "--incognito", "--disable-logging"]
        options_line = " ".join(options)
        cmd = f"chromium http://127.0.0.1:5000/platform {options_line}"
        os.system(f'/bin/bash -c "{cmd} &> /dev/null"')

    threading.Thread(target=_start_chrome, args=(), daemon=True).start()


class Server:
    def __init__(self, hal):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "secret!"
        CORS(self.app)

        self.sio = SocketIO(
            self.app,
            logger=False,
            engineio_logger=False,
            async_mode="eventlet",
            cors_allowed_origins="*",
        )

        self.hal = hal

        self.queue = Queue()
        self.background_thread_started = False

        @self.sio.on("connect")
        def connect(*args):
            if not self.background_thread_started:
                self.sio.start_background_task(self.send_queued_data)
                self.background_thread_started = True

        @self.app.route("/")
        def home():
            return "OK"

        @self.app.route("/platform")
        def platform():
            return render_template("display/index.html")

        @self.app.route("/platform/<path:path>")
        def platform_path(path):
            return send_from_directory("templates/display", path)

        @self.app.route("/platform/home/<path:path>")
        def platform_home_path(path):
            return send_from_directory("../../home", path)


    def start(self, socket_port=5000):
        """Starts the server on the given port"""

        def _start_socket(self, port):
            self.sio.run(self.app, host="0.0.0.0", port=port)

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
