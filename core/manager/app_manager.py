import json
import os
import pickle

import redis


class AppManager:
    """Manages the apps"""

    def __init__(self, hal, server):
        """Initializes the app manager"""
        self.name = "app_manager"
        self.hal = hal
        self.server = server
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        self.available_apps = [
            f.name
            for f in os.scandir("home/apps")
            if f.is_dir() and f.name != "__pycache__" and f.name != "template"
        ]
        self.started_apps = {}

        self.data = {}

        self.add_api()

    def list_applications(self) -> list:
        """Lists all available applications"""

        return [
            {
                "name": app_name,
                "started": int(app_name in self.started_apps),
            }
            for app_name in self.available_apps
        ]

    def list_started_applications(self) -> list:
        """Lists all started applications"""

        return [
            {
                "name": app_name,
                "started": 1,
            }
            for app_name in self.started_apps
        ]

    def list_stopped_applications(self) -> list:
        """Lists all stopped applications"""

        return [
            {
                "name": app_name,
                "started": 0,
            }
            for app_name in self.available_apps
            if app_name not in self.started_apps
        ]

    def start_up(self):
        """Starts up the app manager"""
        try:
            if os.path.exists("home/config.json"):
                with open("home/config.json", "r") as f:
                    config = json.load(f)
                    if "applications" in config and "startup" in config["applications"]:
                        for app_name in config["applications"]["startup"]:
                            self.start(app_name)

                    if "applications" in config and "disabled" in config["applications"]:
                        for app_name in config["applications"]["disabled"]:
                            if app_name in self.started_apps:
                                self.stop(app_name)

                            if app_name in self.available_apps:
                                self.available_apps.remove(app_name)
        except Exception as e:
            self.log(f"Failed to start up the applications: {e}", 4)

    def start(self, app_name: str) -> bool:
        """Starts an application"""

        if app_name not in self.available_apps:
            self.log(f"Unknown application '{app_name}'", 3)
            return False

        if app_name in self.started_apps:
            self.log(f"Application '{app_name}' already started", 3)
            return False

        try:
            # Import the python app
            app = __import__(
                f"home.apps.{app_name}.processing", fromlist=[None]
            ).Application(app_name, self.hal, self.server, self)

            # Start the required drivers and subscribe to the required events
            for driver_name in app.requires:
                self.hal.start_driver(driver_name)
                for event in app.requires[driver_name]:
                    self.hal.register_to_driver(driver_name, app, event)

            # Start the python app
            app.start()

            # Start the js app
            self.server.send_data("start_application", {"application_name": app_name})

            # Store the app as a started app
            self.started_apps[app_name] = app
            self.log(f"Started application '{app_name}'", 2)
            self.update_api_listeners()

        except Exception as e:
            self.log(f"Failed to start application '{app_name}': {e}", 4)
            return False

        return True

    def stop(self, app_name: str) -> bool:
        """Stops an application"""

        if app_name not in self.available_apps:
            self.log(f"Unknown application '{app_name}'", 3)
            return False

        if app_name not in self.started_apps:
            self.log(f"Application '{app_name}' not started", 3)
            return False

        try:
            app = self.started_apps[app_name]
            for driver_name in app.requires:
                for event in app.requires[driver_name]:
                    self.hal.unregister_from_driver(driver_name, app, event)

            # Stop the python app
            app.stop()

            # Stop the js app
            self.server.send_data("stop_application", {"application_name": app_name})

            del self.started_apps[app_name]
            self.log(f"Stopped application '{app_name}'", 2)
            self.update_api_listeners()

        except Exception as e:
            self.log(f"Failed to stop application '{app_name}': {e}", 4)
            return False

        return True

    def log(self, content, level=1):
        """Logs via the redis database"""
        data = {"source": self.name, "content": content, "level": level}
        self.db.set(f"log", pickle.dumps(data))
        self.db.publish(f"log", pickle.dumps(data))

    def add_api(self):
        """Adds the App manager api to the server"""

        @self.server.sio.on("start_application")
        def _(data) -> None:
            self.start(data["application_name"])

        @self.server.sio.on("stop_application")
        def _(data) -> None:
            self.stop(data["application_name"])

        @self.server.sio.on("window_loaded")
        def _() -> None:
            for app_name in self.started_apps.keys():
                self.server.send_data(
                    "start_application", {"application_name": app_name}
                )

        @self.server.sio.on("get_started_applications")
        def _() -> None:
            self.server.send_data(
                "started_applications",
                {"applications": self.list_started_applications()},
            )

        @self.server.sio.on("get_stopped_applications")
        def _() -> None:
            self.server.send_data(
                "stopped_applications",
                {"applications": self.list_stopped_applications()},
            )

        @self.server.sio.on("get_available_applications")
        def _() -> None:
            self.server.send_data(
                "available_applications", {"applications": self.list_applications()}
            )

    def update_api_listeners(self):
        """Updates the App manager api listeners"""
        self.server.send_data(
            "started_applications",
            {"applications": self.list_started_applications()},
        )

        self.server.send_data(
            "stopped_applications",
            {"applications": self.list_stopped_applications()},
        )

        self.server.send_data(
            "available_applications", {"applications": self.list_applications()}
        )
