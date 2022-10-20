import json
import os
import pickle
import traceback
import redis


class AppManager:
    """Manages the apps"""

    def __init__(self, hal, server):
        """Initializes the app manager"""
        self.service = "core"
        self.name = "app_manager"
        self.hal = hal
        self.server = server
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        self.available_apps = [
            f.name
            for f in os.scandir("home/apps")
            if f.is_dir() and f.name != "__pycache__" and f.name != "template"
        ]

        # Import the apps JSON sub-menus
        self.sub_menu = {}
        for app_name in self.available_apps:
            if os.path.exists(f"home/apps/{app_name}/sub-menu.json"):
                with open(f"home/apps/{app_name}/sub-menu.json", "r") as f:
                    sub_menu_data = json.load(f)
                    self.sub_menu[app_name] = sub_menu_data
        
        self.apps_to_start = []
        self.started_apps = {}
        self.first_start = True

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

                    if "applications" in config and "disabled" in config["applications"]:
                        for app_name in config["applications"]["disabled"]:
                            if app_name in self.started_apps:
                                self.stop(app_name)

                            if app_name in self.available_apps:
                                self.available_apps.remove(app_name)

                    if "applications" in config and "startup" in config["applications"]:
                        for app_name in config["applications"]["startup"]:
                            self.apps_to_start.append(app_name)
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
            
            # Stopping apps not required
            if app.is_exclusive:
                started_apps_list = list(self.started_apps.keys())
                for started_app_name in started_apps_list:
                    if started_app_name not in app.applications_allowed and started_app_name != app_name:
                        self.stop(started_app_name)
                for app_required in app.applications_required:
                    if app_required in self.available_apps and app_required not in self.started_apps:
                        self.start(app_required)
            
            # Activating the specified sub-menu
            if app_name in self.sub_menu:
                self.server.send_data(
                    f"{self.service}-{self.name}-add_sub_menu",
                    {"app_name": app_name, "options": self.sub_menu[app_name]}
                )

            # Start the required drivers and subscribe to the required events
            for driver_name in app.requires:
                self.hal.start_driver(driver_name)
                for event in app.requires[driver_name]:
                    self.hal.register_to_driver(driver_name, app, event)

            # Start the python app
            app.start()

            # Start the js app
            self.server.send_data(f"{self.service}-{self.name}-start_application", {"application_name": app_name})

            # Store the app as a started app
            self.started_apps[app_name] = app
            self.log(f"Started application '{app_name}'", 2)
            self.update_api_listeners()

        except Exception:
            self.log(
                f"Failed to start application '{app_name}': {traceback.format_exc()}", 4
            )
            return False

        return True

    def stop(self, app_name: str) -> bool:
        """Stops an application"""

        if app_name not in self.available_apps:
            self.log(f"Unknown application '{app_name}'", 3)
            return False

        # Disactivating the specified sub-menu
        if app_name in self.sub_menu:
            self.server.send_data(
                "core-app_manager-remove_sub_menu",
                {"element_name": app_name}
            )

        if app_name not in self.started_apps:
            self.log(f"Application '{app_name}' not started, could not stop", 3)
            return False

        try:
            app = self.started_apps[app_name]
            for driver_name in app.requires:
                for event in app.requires[driver_name]:
                    self.hal.unregister_from_driver(driver_name, app, event)

            # Stop the python app
            app.stop()

            # Stop the js app
            self.server.send_data(f"{self.service}-{self.name}-stop_application", {"application_name": app_name})

            del self.started_apps[app_name]
            self.log(f"Stopped application '{app_name}'", 2)
            self.update_api_listeners()

        except Exception as e:
            self.log(f"Failed to stop application '{app_name}': {e}", 4)
            return False

        return True

    def log(self, content, level=1):
        """Logs via the redis database"""
        data = {
            "service": "core",
            "source": self.name,
            "content": content,
            "level": level,
        }
        self.db.set(f"log", pickle.dumps(data))
        self.db.publish(f"log", pickle.dumps(data))

    def log_for_application(self, source, content, level=1):
        """Logs via the redis database"""
        data = {
            "service": "application",
            "source": source,
            "content": content,
            "level": level,
        }
        self.db.set(f"log", pickle.dumps(data))
        self.db.publish(f"log", pickle.dumps(data))

    def add_api(self):
        """Adds the App manager api to the server"""

        @self.server.sio.on(f"{self.service}-{self.name}-start_application")
        def _(data) -> None:
            self.start(data["application_name"])

        @self.server.sio.on(f"{self.service}-{self.name}-stop_application")
        def _(data) -> None:
            self.stop(data["application_name"])

        @self.server.sio.on(f"{self.service}-{self.name}-start_option")
        def _(data) -> None:
            self.server.sio.emit(self.sub_menu[data["app_name"]][data["option_name"]]["event_name"], True)

        @self.server.sio.on(f"{self.service}-{self.name}-stop_option")
        def _(data) -> None:
            self.server.sio.emit(self.sub_menu[data["app_name"]][data["option_name"]]["event_name"], False)
        
        @self.server.sio.on(f"{self.service}-{self.name}-trigger_option")
        def _(data) -> None:
            self.server.sio.emit(self.sub_menu[data["app_name"]][data["option_name"]]["event_name"])

        @self.server.sio.on(f"{self.service}-{self.name}-window_loaded")
        def _() -> None:
            if self.first_start:
                for app_name in self.apps_to_start:
                    self.start(app_name)

                self.first_start = False
            else:
                for app_name in self.started_apps:
                    self.server.send_data(
                        f"{self.service}-{self.name}-start_application", {"application_name": app_name}
                    )

        @self.server.sio.on(f"{self.service}-{self.name}-get_started_applications")
        def _() -> None:
            self.server.send_data(
                f"{self.service}-{self.name}-started_applications",
                {"applications": self.list_started_applications()},
            )

        @self.server.sio.on(f"{self.service}-{self.name}-get_stopped_applications")
        def _() -> None:
            self.server.send_data(
                f"{self.service}-{self.name}-stopped_applications",
                {"applications": self.list_stopped_applications()},
            )

        @self.server.sio.on(f"{self.service}-{self.name}-get_available_applications")
        def _() -> None:
            self.server.send_data(
                f"{self.service}-{self.name}-available_applications", {"applications": self.list_applications()}
            )

        @self.server.sio.on(f"{self.service}-{self.name}-log_for_application_manager")
        def _(data) -> None:
            self.log(data["content"], data["level"])

        @self.server.sio.on(f"{self.service}-{self.name}-log_for_application")
        def _(data: dict):
            self.log_for_application(data["source"], data["content"], data["level"])

    def update_api_listeners(self):
        """Updates the App manager api listeners"""
        self.server.send_data(
            f"{self.service}-{self.name}-started_applications",
            {"applications": self.list_started_applications()},
        )

        self.server.send_data(
            f"{self.service}-{self.name}-stopped_applications",
            {"applications": self.list_stopped_applications()},
        )

        self.server.send_data(
            f"{self.service}-{self.name}-available_applications", {"applications": self.list_applications()}
        )
