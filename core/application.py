import pickle
import redis
import threading

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

        self.started = False

        self.db = redis.Redis(host='localhost', port=6379, db=0)

    def subscriber(self, source, event):
        """Listen to events from the driver"""
        ps = self.db.pubsub()
        ps.subscribe(f"{source}_{event}")
        for binary_data in ps.listen():
            try:
                self.listener(source, event, pickle.loads(bytes(binary_data['data'])))
            except Exception as e:
                pass
            if not self.started:
                break


    def listener(self, source, event, data) -> None:
        """
        Gets notified when some data (named "event")
        of a driver ("source") is updated
        """
        if source not in self.requires:
            self.hal.log(f"{self.name}: subscribed to an unrequested event.")
            return
        if event not in self.requires[source]:
            self.hal.log(f"{self.name}: not subscrbed to {event} from {source}")
            return

        if not self.started:
            return
        # Write your code here (what to do when the data is recieved)


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
