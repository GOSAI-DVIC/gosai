import pickle
import redis
import threading
import traceback

class BaseApplication(threading.Thread):
    """Template class for applications"""

    def __init__(self, name, hal, server, manager):
        threading.Thread.__init__(self)
        self.name = name
        self.hal = hal
        self.server = server
        self.manager = manager

        self.requires = {} # Select what driver you want to use
        self.data = {} # data that is sent to the js script
        self.is_exclusive = False # if true, close the other applications except the specified ones
        self.started = False
        self.applications_allowed = []
        self.applications_required = []

        self.db = redis.Redis(host='localhost', port=6379, db=0)

    def subscriber(self, source, event):
        """Listen to events from the driver"""
        ps = self.db.pubsub()
        ps.subscribe(f"{source}_{event}")
        for binary_data in ps.listen():
            try:
                self.listener(source, event, pickle.loads(bytes(binary_data['data']))["data"])
            except pickle.UnpicklingError as e:
                continue
            except Exception:
                self.log(f"Error in listener: {traceback.format_exc()}", 4)
                self.manager.stop(self.name)
            if not self.started:
                break


    def listener(self, source, event, data) -> None:
        """
        Gets notified when some data (named "data")
        of a driver's event ("source" and "event") is updated
        """
        if not self.started:
            return

        if source not in self.requires:
            self.log(f"Subscribed to an unrequested source: {source}", 3)
            return
        if event not in self.requires[source]:
            self.log(f"Subscribed to an unrequested event: {event} from {source} but gett", 3)
            return

        if not self.started:
            return
        # Write your code here (what to do when the data is recieved)

    def get_driver_event_data(self, driver, event):
        """Gets the data of a driver's event"""
        data = self.db.get(f"{driver}_{event}")
        if data == b'':
            return None
        else:
            unpickled_data = pickle.loads(data)
            return unpickled_data["data"]

    def execute(self, driver, action, data):
        """
        Executes an action of a driver
        - 'driver' is the name of the driver
        - 'action' is the name of the action
        - 'data' is the data that will be sent to the driver's callback
        """
        self.db.publish(f"{driver}_exec_{action}", pickle.dumps(data))

    def stop(self):
        """Stops the application"""
        self.started = False

    def run(self):
        """Thread that runs the application"""
        self.started = True
        for driver in self.requires:
            for event in self.requires[driver]:
                threading.Thread(target=self.subscriber, args=(driver, event)).start()

    def __str__(self):
        return str(self.name)

    def log(self, content, level=1):
        """Logs via the redis database"""
        data = {"service": "application", "source": self.name, "content": content, "level": level}
        self.db.set("log", pickle.dumps(data))
        self.db.publish("log", pickle.dumps(data))
