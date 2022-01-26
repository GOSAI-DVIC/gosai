import datetime
import os

LOGS_PATH = "core/hal/logs"

class AppManager:
    """Manages the apps"""

    def __init__(self, hal, server):
        """Initializes the app manager"""
        self.hal = hal
        self.server = server

        self.name = "app_manager"
        self.available_apps = [
            f.name
            for f in os.scandir("platform/apps")
            if f.is_dir() and f.name != "__pycache__" and f.name != "template"
        ]
        self.started_apps = {}

        self.data = {}

        @self.server.sio.on("start_application")
        def _(data) -> None:
            self.start(data["application_name"])

        @self.server.sio.on("stop_application")
        def _(data) -> None:
            self.stop(data["application_name"])

    def list_applications(self) -> list:
        """Lists all available applications"""

        return self.available_apps

    def list_started_applications(self) -> list:
        """Lists all started applications"""

        return list(self.started_apps.keys())

    def list_stopped_applications(self) -> list:
        """Lists all stopped applications"""

        return [
            app_name
            for app_name in self.available_apps
            if app_name not in self.started_apps
        ]

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
                f"platform.apps.{app_name}.processing", fromlist=[None]
            ).Application(app_name, self.hal, self.server, self)

            # Start the required drivers and subscribe to the required events
            for driver_name in app.requires:
                self.hal.start_driver(driver_name)
                for event in app.requires[driver_name]:
                    self.hal.register_to_driver(driver_name, app, event)

            # Start the python app
            app.start()

            # Start the js app
            self.server.send_data(
                "start_application", {"application_name": app_name}
            )

            # Store the app as a started app
            self.started_apps[app_name] = app
            self.log(f"Started application '{app_name}'", 2)

        except Exception as e:
            self.log(
                f"Failed to start application '{app_name}': {e}", 4
            )
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
                    self.hal.unregister_from_driver(
                        driver_name, app, event
                    )

            # Stop the python app
            app.stop()

            # Stop the js app
            self.server.send_data(
                "stop_application", {"application_name": app_name}
            )

            del self.started_apps[app_name]
            self.log(f"Stopped application '{app_name}'", 2)

        except Exception as e:
            self.log(
                f"Failed to stop application '{app_name}': {e}", 4
            )
            return False

        return True

    def log(self, message, level=1):
        """Logs a message"""
        if level >= int(os.environ["LOG_LEVEL"]):
            print(f"{self.name}: {message}")

        with open(f"{LOGS_PATH}/app_manager.log", "a+") as log:
            log.write(
                f"{datetime.datetime.now().strftime('%b-%d-%G-%I:%M:%S%p')} : {message}\n"
            )
