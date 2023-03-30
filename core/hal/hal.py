# Hardware Abstraction Layer

import os
import pickle
import threading
from typing import Any, Dict, List

import redis

DRIVERS_PATH = "core/hal/drivers"


class HardwareAbstractionLayer:
    """Main interface to access the drivers. Tracks the state of
    the drivers. Should be used by the apps or any entity to
    access the drivers data if the entity is not registered
    to any event of the driver.

    Attributes
    ----------
    name : str
        The name of this object. Used for logging purposes.
    server : Server
        The server object. Augments its API.
    db : Redis
        The redis database through which each independent
        object can communicate.
    available_drivers : list
        A list of available drivers. Generated from the
        drivers folder.
    drivers : dict
        A dictionary of drivers. The keys are the driver names.

    Methods
    -------
    init_driver(driver_name: str) -> bool
        Initializes a driver instance.
    start_driver(driver_name: str) -> bool
        Starts a driver and the drivers it requires. Initializes
        it if it is not already.
    monitor_driver_stopping()
        Monitors when a driver is stopped to update the api
    register_to_driver(driver_name: str, entity: str, event: str) -> bool
        Registers an entity to an event of a driver.
    unregister_from_driver(driver_name: str, entity: str, event: str) -> bool
        Unregisters an entity from an event of a driver.
    get_driver_event_data(driver_name: str, event: str) -> Any
        Returns the data of an event of a driver.
    get_started_drivers() -> list
        Returns a list of started drivers.
    get_stopped_drivers() -> list
        Returns a list of stopped drivers.
    get_drivers() -> list
        Returns a list of all drivers.
    log(content: str, level: int)
        Logs a message. Uses the redis database to communicate with the
        logger.
    add_api()
        Adds the API to the server. Should only run once.
    update_api_listeners()
        Updates the api listeners to reflect the current state of the drivers.
    """

    def __init__(self, server):
        self.service = "core"
        self.name = "hal"
        self.server = server
        self.db = redis.Redis(host="localhost", port=6379, db=0)

        self.log(f"Starting {self.name}")
        self.available_drivers = [
            f.path.split("/")[-1]
            for f in os.scandir(DRIVERS_PATH)
            if f.is_dir() and f.path.split("/")[-1] != "__pycache__"
        ]
        print("available drivers : ",self.available_drivers)

        self.drivers = {}

        self.add_api()
        self.monitor_driver_stopping()

        # for driver_name in self.available_drivers:

    def init_driver(self, driver_name: str) -> bool:
        """Initializes a driver

        Parameters
        ----------
        driver_name : str
            The name of the driver to initialize.

        Returns
        -------
        bool
            True if the driver was initialized, False otherwise.
        """
        if driver_name not in self.available_drivers:
            self.log(f"Cannot init: {driver_name} is not a valid driver", 3)
            return False

        try:
            driver = __import__(
                f"{DRIVERS_PATH.replace('/', '.')}.{driver_name}.{driver_name}",
                fromlist=[None],
            ).Driver(driver_name, self)
            self.drivers[driver_name] = driver
        except Exception as e:
            self.log(f"Cannot init {driver_name}: {e}", 4)
            return False

        return True

    def start_driver(self, driver_name: str) -> bool:
        """Starts a driver and all its dependecies

        Parameters
        ----------
        driver_name : str
            The name of the driver to start.

        Returns
        -------
        bool
            True if the driver was started, False otherwise.
        """
        if driver_name not in self.available_drivers:
            self.log(f"{driver_name} is not a valid driver", 3)
            return False

        if driver_name not in self.drivers:
            self.init_driver(driver_name)
        print(self.drivers)
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

        self.update_api_listeners()
        return True

    def monitor_driver_stopping(self):
        """Monitors when a driver is stopped to update the api

        This method is called by the init method. It monitors the
        redis database for when a driver is stopped. When it is
        stopped, it updates the api listeners to reflect the current
        state of the drivers.
        """

        def _monitor_driver_stopping():
            ps = self.db.pubsub()
            ps.subscribe(f"driver_stopped")
            for msg in ps.listen():
                try:
                    driver_name = pickle.loads(msg["data"])["driver_name"]
                    self.update_api_listeners()
                except Exception as e:
                    pass

        threading.Thread(target=_monitor_driver_stopping).start()

    def register_to_driver(self, driver_name: str, entity: str, event: str) -> bool:
        """Registers an entity to an event of a driver

        Parameters
        ----------
        driver_name : str
            The name of the driver to register to.
        entity : str
            The name of the entity to register.
        event : str
            The name of the event to register to.

        Returns
        -------
        bool
            True if the entity was registered, False otherwise.
        """
        if driver_name not in self.drivers:
            if driver_name not in self.available_drivers:
                self.log(f"Cannot register: {driver_name} is not a valid driver", 3)
                return False
            self.init_driver(driver_name)

        self.drivers[driver_name].register(entity, event)
        self.update_api_listeners()
        return True

    def unregister_from_driver(self, driver_name: str, entity: str, event: str) -> bool:
        """Unregisters an entity from an event of a driver

        Parameters
        ----------
        driver_name : str
            The name of the driver to unregister from.
        entity : str
            The name of the entity to unregister.
        event : str
            The name of the event to unregister from.

        Returns
        -------
        bool
            True if the entity was unregistered, False otherwise.
        """
        if driver_name not in self.drivers:
            self.log(f"Cannot unregister: {driver_name} is not a valid driver", 3)
            return False

        self.drivers[driver_name].unregister(entity, event)
        self.update_api_listeners()
        return True

    def get_driver_event_data(self, driver_name: str, event: str) -> Any:
        """Returns the data of an event of a driver

        Parameters
        ----------
        driver_name : str
            The name of the driver to get the data from.
        event : str
            The name of the event to get the data from.

        Returns
        -------
        Any
            The data of the event.
        """
        if driver_name not in self.drivers:
            self.log(f"Cannot get data: {driver_name} is not a valid driver", 3)
            return None
        return self.drivers[driver_name].get_event_data(event)

    def get_started_drivers(self) -> List[Dict]:
        """Returns a list of drivers that are started

        Returns
        -------
        List[Dict]
            A list of drivers that are started. Each driver is a dict
            with the following keys:
                - name: The name of the driver
                - started: 1 if the driver is started, 0 otherwise
                - registered_entities: A list of entities that are
                    registered to the driver
        """
        started_drivers = []
        for driver_name, driver in self.drivers.items():
            if driver.started.value and not driver.paused.value:
                registered_entities = {
                    event: [entity.name for entity in driver.registered[event]]
                    for event in driver.registered
                }

                started_drivers.append(
                    {
                        "name": driver_name,
                        "started": 1,
                        "registered_entities": registered_entities,
                    }
                )
        return started_drivers

    def get_stopped_drivers(self) -> List[Dict]:
        """Returns a list of drivers that are stopped

        Returns
        -------
        List[Dict]
            A list of drivers that are stopped. Each driver is a dict
            with the following keys:
                - name: The name of the driver
                - started: 1 if the driver is started, 0 otherwise
                - registered_entities: A list of entities that are
                    registered to the driver
        """
        stopped_drivers = []
        for driver_name, driver in self.drivers.items():
            if not driver.started.value or driver.paused.value:
                registered_entities = {
                    event: [entity.name for entity in driver.registered[event]]
                    for event in driver.registered
                }
                stopped_drivers.append(
                    {
                        "name": driver_name,
                        "started": 0,
                        "registered_entities": registered_entities,
                    }
                )
        for driver_name in self.available_drivers:
            if driver_name not in self.drivers:
                stopped_drivers.append(
                    {
                        "name": driver_name,
                        "started": 0,
                        "registered_entities": {},
                    }
                )
        return stopped_drivers

    def get_drivers(self) -> List[Dict]:
        """Returns a list of available drivers

        Returns
        -------
        List[Dict]
            A list of drivers. Each driver is a dict with the following keys:
                - name: The name of the driver
                - started: 1 if the driver is started, 0 otherwise
                - registered_entities: A list of entities that are
                    registered to the driver
        """
        available_drivers = self.get_started_drivers() + self.get_stopped_drivers()
        return available_drivers

    def log(self, content, level=1):
        """Logs via the redis database

        Parameters
        ----------
        content : str
            The content to log.

        level : int, optional
            The level of the log. (default is 1)
        """
        data = {
            "service": "core",
            "source": self.name,
            "content": content,
            "level": level,
        }
        self.db.set(f"log", pickle.dumps(data))
        self.db.publish(f"log", pickle.dumps(data))

    def add_api(self):
        """Adds the Hal api to the server"""

        @self.server.sio.on(f"{self.service}-{self.name}-get_started_drivers")
        def _():
            self.server.send_data(
                f"{self.service}-{self.name}-started_drivers", {"drivers": self.get_started_drivers()}
            )

        @self.server.sio.on(f"{self.service}-{self.name}-get_stopped_drivers")
        def _():
            self.server.send_data(
                f"{self.service}-{self.name}-stopped_drivers", {"drivers": self.get_stopped_drivers()}
            )

        @self.server.sio.on(f"{self.service}-{self.name}-get_available_drivers")
        def _():
            self.server.send_data(f"{self.service}-{self.name}-available_drivers", {"drivers": self.get_drivers()})

    def update_api_listeners(self):
        """Updates the Hal api listeners to match the current
        state of the drivers.

        This is called when a driver is started or stopped.
        """
        self.server.send_data(
            f"{self.service}-{self.name}-started_drivers", {"drivers": self.get_started_drivers()}
        )
        self.server.send_data(
            f"{self.service}-{self.name}-stopped_drivers", {"drivers": self.get_stopped_drivers()}
        )
        self.server.send_data(f"{self.service}-{self.name}-available_drivers", {"drivers": self.get_drivers()})
