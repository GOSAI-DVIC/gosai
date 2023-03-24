import datetime as dt
import os
import pickle
import random
import threading
import time
from queue import Queue

from dotenv import load_dotenv
from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import redis


def start_chrome(path):
    """Launch a chrome browser to display the platform"""

    def _start_chrome(path):
        options = ["--start-fullscreen", "--incognito", "--disable-logging"]
        options_line = " ".join(options)
        cmd = f"chromium http://127.0.0.1:8000/{path}/platform {options_line}"
        os.system(f'/bin/bash -c "{cmd} &> /dev/null"')

    threading.Thread(target=_start_chrome, args=(path,), daemon=True).start()


class Server:
    """Main server class"""

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "secret!"
        CORS(self.app)
        self.db = redis.Redis(host="127.0.0.1", port=6379, db=0)
        self.name = "server"
        self.service = "core"

        load_dotenv("home/.env")
        platform_name = os.getenv("PLATFORM")
        if platform_name is None:
            self.log("No platform name found in .env file", 3)
            platform_name = "default"

        self.base_path = f"gosai/{platform_name}"

        self.sio = SocketIO(
            self.app,
            path=f"{self.base_path}/socket.io",
            logger=False,
            engineio_logger=False,
            async_mode="eventlet",
            cors_allowed_origins="*",
        )

        self.clients = {}

        self.queue = Queue()
        self.background_thread_started = False

        self.control_password = "314159"

        self.path = self.base_path

        create_socket_api(self)
        create_flask_api(self)

    def daily_control_password_generator(self):
        """Generate daily a 6 digits password to access /control"""

        def _daily_control_password_generator(self):
            self.control_password = str(random.randint(0, 999999)).zfill(6)
            time.sleep(_waitToTomorrow())

        def _waitToTomorrow():
            """Wait to tomorrow 00:00 am."""
            tomorrow = dt.datetime.replace(
                dt.datetime.now() + dt.timedelta(days=1), hour=0, minute=0, second=0
            )
            delta = tomorrow - dt.datetime.now()
            return delta.seconds

        threading.Thread(
            target=_daily_control_password_generator, args=(self,), daemon=True
        ).start()

    def generate_control_password(self):
        """Generate a 6 digits password to access /control"""
        self.control_password = str(random.randint(0, 999999)).zfill(6)

    def start(self, socket_port=8000):
        """Starts the server on the given port"""

        def _start_socket(self, port):
            self.sio.run(self.app, host="0.0.0.0", port=port)

        self.daily_control_password_generator()

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
                try:
                    self.sio.emit(name, data)
                except:
                    print("Error while sending data, passing error")
                    pass
                    

    def log(self, content, level=1):
        """Logs via the redis database"""
        data = {
            "service": "core",
            "source": "server",
            "content": content,
            "level": level,
        }
        self.db.set("log", pickle.dumps(data))
        self.db.publish("log", pickle.dumps(data))


def create_socket_api(server: Server):
    """Create the socketio api."""
    @server.sio.on("connect")
    def connect(*_):
        server.clients[request.sid] = {
            "address": request.remote_addr,
            "source": request.args.get("source"),
            "time": dt.datetime.now().strftime("%b-%d-%G-%I:%M:%S%p"),
        }
        server.sio.emit(f"{server.service}-{server.name}-connected_users", {"users": server.clients})
        if not server.background_thread_started:
            server.background_thread_started = True
            server.sio.start_background_task(server.send_queued_data)

    @server.sio.on("disconnect")
    def disconnect():
        del server.clients[request.sid]
        server.sio.emit(f"{server.service}-{server.name}-connected_users", {"users": server.clients})

    @server.sio.on(f"{server.service}-{server.name}-get_users")
    def get_users():
        server.sio.emit(f"{server.service}-{server.name}-connected_users", {"users": server.clients})

    @server.sio.on(f"{server.service}-{server.name}-get_control_password")
    def get_control_password():
        server.sio.emit(
            f"{server.service}-{server.name}-control_password",
            {"control_password": server.control_password},
            room=request.sid,
        )

    @server.sio.on(f"{server.service}-{server.name}-generate_control_password")
    def generate_control_password():
        server.generate_control_password()
        server.sio.emit(
            f"{server.service}-{server.name}-control_password",
            {"control_password": server.control_password},
            room=request.sid,
        )

    @server.sio.on(f"{server.service}-{server.name}-check_control_password")
    def check_control_password(data: dict):
        check = False
        if data["control_password"] == server.control_password:
            check = True
        server.sio.emit(
            f"{server.service}-{server.name}-checked_control_password", {"checked": check}, room=request.sid
        )

    #receive audio from client and put it in the redis database
    @server.sio.on("web_audio")
    def audio(data):
        
        audio_data = {
            "name": "audio_bytes",
            "channel": 1,
            "data": []
            
        }

        audio_data["data"] = data

        driver = "web_audio_stream"
        action = "audio_conversion"

        server.db.publish(f"{driver}_exec_{action}", pickle.dumps(audio_data))
  
    
        #print(data)

    # @server.sio.on(f"{server.service}-{server.name}-audio", {"audio": server.audio})
    # def _():
    #     server.log(server.audio)

    @server.sio.on(f"{server.service}-{server.name}-sound")
    def _():
        server.sio.emit(f"{server.service}-{server.name}-sound")

def create_flask_api(server: Server):
    """Create the flask api. This is used for the web interface"""
    @server.app.route("/gosai")
    def home():
        return "OK"

    @server.app.route(f"/{server.base_path}/platform")
    def platform():
        return render_template("display/index.html")

    @server.app.route(f"/{server.base_path}/platform/<path:path>")
    def platform_path(path):
        return send_from_directory("templates/display", path)

    @server.app.route(f"/{server.base_path}/platform/home/<path:path>")
    def platform_home_path(path):
        return send_from_directory("../../home", path)

    @server.app.route(f"/{server.base_path}/core/<path:path>")
    def platform_core_server_path(path):
        return send_from_directory("../../core/", path)

    @server.app.route(f"/{server.base_path}/control")
    def control():
        return render_template("control/index.html")

    @server.app.route(f"/{server.base_path}/control/<path:path>")
    def control_path(path):
        return send_from_directory("templates/control", path)

    @server.app.route(f"/{server.base_path}/dashboard")
    def dashboard():
        return render_template("dashboard/index.html")

    @server.app.route(f"/{server.base_path}/dashboard/<path:path>")
    def dashboard_path(path):
        return send_from_directory("templates/dashboard", path)

    @server.app.route(f"/{server.base_path}/core/<path:path>")
    def core_path(path):
        return send_from_directory("../", path)
