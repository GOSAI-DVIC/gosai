# Hardware Abstraction Layer

import datetime
import os
from typing import Any

DRIVERS_PATH = "core/hal/drivers"
LOGS_PATH = "core/hal/logs"


class HardwareAbstractionLayer:
    """
    Main interface to access the drivers
    Should be used by the apps to access the drivers
    """

    def __init__(self):

        self.name = "hal"
        self.log(f"Starting {self.name}")
        self.available_drivers = [
            f.path.split("/")[-1]
            for f in os.scandir(DRIVERS_PATH)
            if f.is_dir() and f.path.split("/")[-1] != "__pycache__"
        ]

        self.drivers = {}

        for driver_name in self.available_drivers:
            if driver_name not in self.drivers:
                self.init_driver(driver_name)

    def init_driver(self, driver_name: str) -> bool:
        """
        Initializes a driver
        """
        if driver_name not in self.available_drivers:
            self.log(f"Cannot init: {driver_name} is not a valid driver", 3)
            return False

        driver = __import__(
            f"{DRIVERS_PATH.replace('/', '.')}.{driver_name}.{driver_name}",
            fromlist=[None],
        ).Driver(driver_name, self)
        self.drivers[driver_name] = driver

        return True

    def start_driver(self, driver_name: str) -> bool:
        """
        Starts a driver and all its dependecies
        """
        if driver_name not in self.available_drivers:
            self.log(f"{driver_name} is not a valid driver", 3)
            return False

        driver = self.drivers[driver_name]

        if not driver.started.value or driver.paused.value:
            for req_driver_name in driver.requires:
                if req_driver_name not in self.available_drivers:
                    self.log(
                        f"Driver '{req_driver_name}' is required \
                            by '{driver.name}' but is not valid",
                        3,
                    )
                    return False
                self.start_driver(req_driver_name)
            if not driver.started.value:
                driver.launch()
            if driver.paused.value:
                driver.resume()

        return True

    def register_to_driver(self, driver_name: str, entity: str, event: str) -> bool:
        """
        Registers an entity to an event of a driver
        """
        if driver_name not in self.drivers:
            if driver_name not in self.available_drivers:
                self.log(f"Cannot register: {driver_name} is not a valid driver", 3)
                return False
            self.init_driver(driver_name)

        self.drivers[driver_name].register(entity, event)

        return True

    def unregister_from_driver(self, driver_name: str, entity: str, event: str) -> bool:
        """
        Unregisters an entity from an event of a driver
        """
        if driver_name not in self.drivers:
            self.log(f"Cannot unregister: {driver_name} is not a valid driver", 3)
            return False

        self.drivers[driver_name].unregister(entity, event)

        return True

    def get_driver_event_data(self, driver_name: str, event: str) -> Any:
        """
        Returns the data of an event of a driver
        """
        if driver_name not in self.drivers:
            self.log(f"Cannot get data: {driver_name} is not a valid driver", 3)
            return False

        return self.drivers[driver_name].get_event_data(event)

    def get_started_drivers(self) -> str:
        """Returns a list of drivers that are started"""
        started_drivers = []
        for driver_name, driver in self.drivers.items():
            if driver.started.value and not driver.paused.value:
                started_drivers.append(driver_name)
        return started_drivers

    def get_stopped_drivers(self) -> str:
        """Returns a list of drivers that are stopped"""
        stopped_drivers = []
        for driver_name, driver in self.drivers.items():
            if not driver.started.value or driver.paused.value:
                stopped_drivers.append(driver_name)
        return stopped_drivers

    def get_drivers(self) -> str:
        """Returns a list of available drivers"""
        return self.available_drivers

    def log(self, message, level=1):
        """
        Logs every things (for now in the console)
        TODO: create a temporary log file
        """
        if level >= int(os.environ["LOG_LEVEL"]):
            print(f"{self.name}: {message}")

        with open(f"{LOGS_PATH}/{self.name}.log", "a+") as log:
            log.write(
                f"{datetime.datetime.now().strftime('%b-%d-%G-%I:%M:%S%p')} : {message}\n"
            )
