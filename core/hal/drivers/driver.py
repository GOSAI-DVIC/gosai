# Base driver template

import pickle
import threading
import time
import traceback
from multiprocessing import Process, Value
from typing import Any

import redis


class BaseDriver(Process):
    """Base class for all drivers"""

    def __init__(self, name, parent):
        super().__init__()
        # threading.Thread.__init__(self)
        self.name = name
        self.parent = parent
        self.commands = {}
        self.type = "loop"
        self.started = Value("i", 0)  # False
        self.paused = Value("i", 0)  # False
        self.registered = {}  # Lists of entities registered to each events
        self.requires = {}
        self.db = redis.Redis(host="localhost", port=6379, db=0)
        self.callbacks = {}

    def execute(self, command, arguments):
        """Executes a command with the given arguments"""

        self.log(f"Executing command '{command}' with arguments '{arguments}'", 2)

    def launch(self):
        """
        Sets the started flag and starts the driver
        """
        self.started.value = 1
        self.start()

    def pre_run(self):
        """
        Runs once at the start of the driver
        """
        self.db = redis.Redis(host="localhost", port=6379, db=0)

    def run(self):
        """Runs when the thread is started"""
        try:
            self.pre_run()
        except Exception:
            self.log(f"Error when starting the driver: {traceback.format_exc()}", 4)
            return
        # Starts the required drivers
        self.log("Driver running", 2)
        loop_times = []
        while 1:
            try:
                if not self.paused.value and self.type != "no_loop":
                    start_t = time.time()
                    self.loop()
                    end_t = time.time()
                    loop_times.append(1000 * (end_t - start_t))
                    if len(loop_times) == 5:
                        if not self.paused.value:
                            self.record_performance(
                                "loop_time", sum(loop_times) / len(loop_times)
                            )
                        loop_times = []
                else:
                    time.sleep(0.5)

            except Exception:
                self.log(f"Error when running the driver: {traceback.format_exc()}", 4)
                return

    def loop(self):
        """
        The main loop of the driver.
        Should be overwritten by the driver
        """
        time.sleep(0.5)

    def resume(self):
        """Resumes the driver"""

        self.log("Driver resumed", 2)

        for driver_name, event_list in self.requires.items():
            for event in event_list:
                self.parent.register_to_driver(driver_name, self, event)
        self.paused.value = 0

    def stop(self):
        """Stops the driver"""

        self.log("Driver paused", 2)

        for driver_name, event_list in self.requires.items():
            for event in event_list:
                self.parent.unregister_from_driver(driver_name, self, event)

        self.paused.value = 1
        # Notify the parent that the driver is stopped
        self.db.publish("driver_stopped", pickle.dumps({"driver_name": self.name}))
        self.record_performance("loop_time", 0)

    def create_event(self, event) -> bool:
        """Adds an event to the driver"""
        if event in self.registered:
            self.log(f"Tried to add an already existing event '{event}'", 3)
            return False

        self.log(f"Creating event '{event}'", 2)
        self.registered[event] = []

        self.db.set(f"{self.name}_{event}", "")

        return True

    def set_event_data(self, event, data):
        """Adds data to the driver and notifies the listeners"""

        if event not in self.registered:
            self.log(f"Tried to add data for an unknown event '{event}'", 3)
            return False

        payload = pickle.dumps({
            "data": data,
            "emit_time": time.time(),
        })

        self.db.set(f"{self.name}_{event}", payload)
        self.db.publish(f"{self.name}_{event}", payload)
        return True

    def get_event_data(self, event):
        """Returns the data of an event"""

        if event not in self.registered:
            self.log(f"Tried to get data for an unknown event '{event}'", 3)
            return None

        try:
            payload = pickle.loads(self.db.get(f"{self.name}_{event}"))
            data = payload["data"]
            # delta_time = time.time() - payload["emit_time"]
            # print(f"From: {self.name} {event} Delta time: {delta_time}")
            return data
        except Exception:
            return None

    def register_to_driver(self, driver_name, event):
        """
        Registers this driver to the event of another driver.
        """
        if driver_name not in self.requires:
            self.requires[driver_name] = []
        self.requires[driver_name].append(event)
        self.parent.register_to_driver(driver_name, self, event)

    def register(self, entity, event):
        """Registers an entity instance to a driver's event"""

        self.log(f"Registering entity '{entity}' to '{event}'", 2)
        if event in self.registered:
            self.registered[event].append(entity)
        else:
            self.registered[event] = [entity]

    def unregister(self, entity, event) -> bool:
        """Unregisters an application instance from a driver's event"""

        if event not in self.registered:
            self.log(f"{entity} tried to unregister from an unknown event '{event}'", 3)
            return False

        self.log(f"Unregistering entity '{entity}' from '{event}'", 2)
        self.registered[event].remove(entity)

        # Checks if someone is still registered to this driver
        for event in self.registered:
            if len(self.registered[event]) > 0:
                return True
        self.log("Pausing driver: no one is subscribed to it anymore", 2)
        self.stop()

        return True

    def notify(self, event) -> bool:
        """Notify every registered app of an event"""
        if event not in self.registered:
            self.log(f"Tried to notify for an unknown event '{event}'", 3)
            return False

        for app in self.registered[event]:
            # app.listener(self.name, event)
            threading.Thread(target=app.listener, args=(self.name, event)).start()

        return True

    def listener(self, source, event) -> bool:
        """
        Gets notified when some data (named "event")
        of a driver ("source") is updated
        """
        if source not in self.requires:
            self.log("Subscribed to an unrequested event.", 3)
            return False
        if event not in self.requires[source]:
            self.log(f"not subscrbed to {event} from {source}", 3)
            return False

    def create_callback(self, action: str, callback: callable) -> bool:
        """
        Creates a callback for an action that can be executed by any source.
        - 'action' is a string that identifies the action to execute.
        - 'callback' is the function that will be called when the action is executed.
            To do so, a message must be sent via the redis server on the channel called
            '{self.name}_exec_{action}'
        """
        self.log(f"Creating callback for action '{action}'", 2)
        if action in self.callbacks:
            self.log(f"Callback already exists for action '{action}'", 3)
            return False

        def _subscriber(self, action: str, callback: callable) -> None:
            ps = self.db.pubsub()
            ps.subscribe(f"{self.name}_exec_{action}")
            for binary_data in ps.listen():
                if action not in self.callbacks:
                    self.log(f"Callback for action '{action}' not needed anymore", 3)
                    return
                try:
                    data = pickle.loads(bytes(binary_data["data"]))

                    def _execute_callback(callback: callable, data) -> None:
                        start_t = time.time()
                        exec_time = callback(data)
                        if not self.paused.value:
                            exec_time = (
                                1000 * (time.time() - start_t)
                                if exec_time is None
                                else exec_time
                            )
                            self.record_performance(action, exec_time)

                    threading.Thread(
                        target=_execute_callback, args=(callback, data)
                    ).start()
                except pickle.UnpicklingError:
                    continue
                except Exception:
                    self.log(f"Error while loading callback data: {traceback.format_exc()}", 3)

        sub = threading.Thread(
            target=_subscriber,
            args=(
                self,
                action,
                callback,
            ),
        )
        self.callbacks[action] = sub
        sub.start()

        return True

    def create_callback_on_event(
        self, action: str, callback: callable, source: str, event: str
    ) -> bool:
        """
        Creates a callback for an action that will be called when an event is triggered.
        - 'action' is a string that identifies the action.
        - 'callback' is the function that will be called when the event from 'source'
            is triggered.
        - 'source' is the name of the driver that will trigger the event.
        - 'event' is the name of the event that will trigger the action.
        """
        self.log(f"Creating callback for action '{action}' on event '{event}'", 2)
        if action in self.callbacks:
            self.log(f"Callback already exists for action '{action}'", 3)
            return False

        if source not in self.requires or event not in self.requires[source]:
            self.register_to_driver(source, event)

        def _subscriber(
            self, action: str, callback: callable, source: str, event: str
        ) -> None:
            ps = self.db.pubsub()
            ps.subscribe(f"{source}_{event}")
            for binary_data in ps.listen():
                if action not in self.callbacks:
                    self.log(f"Callback for action '{action}' not needed anymore", 3)
                    return
                try:
                    if not self.paused.value:
                        payload = pickle.loads(bytes(binary_data["data"]))
                        data = payload["data"]
                        delta_time = time.time() - payload["emit_time"]
                        # print(f"From: {source} {event} Delta time: {delta_time}")

                        def _execute_callback(callback: callable, data) -> None:
                            start_t = time.time()
                            exec_time = callback(data)
                            if not self.paused.value:
                                exec_time = (
                                    1000 * (time.time() - start_t)
                                    if exec_time is None
                                    else exec_time
                                )
                                self.record_performance(action, exec_time)

                        threading.Thread(
                            target=_execute_callback, args=(callback, data)
                        ).start()
                except pickle.UnpicklingError:
                    continue
                except Exception:
                    self.log(f"Error while loading callback data: {traceback.format_exc()}", 3)

        sub = threading.Thread(
            target=_subscriber,
            args=(
                self,
                action,
                callback,
                source,
                event,
            ),
        )
        self.callbacks[action] = sub
        sub.start()

        return True

    def delete_callback(self, action: str) -> bool:
        """
        Deletes a callback for an action
        """
        if action not in self.callbacks:
            self.log(f"Callback does not exist for action '{action}'", 3)
            return False

        del self.callbacks[action]
        return True

    def record_performance(self, record_name: str, data: Any) -> None:
        """
        Records performance data for this driver.
        """
        performance_record = {
            "source": {
                "name": self.name,
                "type": "driver",
            },
            "type": record_name,
            "data": data,
        }
        self.db.set(
            "performance_record",
            pickle.dumps(performance_record),
        )
        self.db.publish(
            "performance_record",
            pickle.dumps(performance_record),
        )

    def log(self, content, level=1):
        """Logs via the redis database"""
        data = {
            "service": "driver",
            "source": self.name,
            "content": content,
            "level": level,
        }
        self.db.set("log", pickle.dumps(data))
        self.db.publish("log", pickle.dumps(data))

    def __str__(self):
        return str(f"driver_{self.name}")
