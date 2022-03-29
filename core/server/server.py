import os
import threading
from queue import Queue

from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

def start_chrome(path):
    def _start_chrome(path):
        options = ["--start-fullscreen", "--incognito", "--disable-logging"]
        options_line = " ".join(options)
        cmd = f"chromium http://127.0.0.1:8000/{path}/platform {options_line}"
        os.system(f'/bin/bash -c "{cmd} &> /dev/null"')

    threading.Thread(target=_start_chrome, args=(path,), daemon=True).start()


class Server:
    """ Main server class """
    def __init__(self, hal):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "secret!"
        CORS(self.app)

        load_dotenv("home/.env")
        platform_name = os.getenv("PLATFORM")
        if platform_name is None:
            self.hal.log("Server: No platform name found in .env file", 3)
            platform_name = "default"

        base_path = f"gosai/{platform_name}"

        self.sio = SocketIO(
            self.app,
            path= f"{base_path}/socket.io",
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

        @self.app.route("/gosai")
        def home():
            return "OK"

        @self.app.route(f"/{base_path}/platform")
        def platform():
            return render_template("display/index.html")

        @self.app.route(f"/{base_path}/platform/<path:path>")
        def platform_path(path):
            return send_from_directory("templates/display", path)

        @self.app.route(f"/{base_path}/platform/home/<path:path>")
        def platform_home_path(path):
            return send_from_directory("../../home", path)

        @self.app.route(f"/{base_path}/control")
        def control():
            return render_template("control/index.html")

        @self.app.route(f"/{base_path}/control/<path:path>")
        def control_path(path):
            return send_from_directory("templates/control", path)

        self.path = base_path


    def start(self, socket_port=8000):
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
