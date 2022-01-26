from apps.application import BaseApplication

class Application(BaseApplication):
    """Poke-It"""

    def __init__(self, name, hal, server, manager):
        super().__init__(name, hal, server, manager)
        self.requires["pose_to_mirror"] = ["mirrored_data"]

    def listener(self, source, event, data):
        super().listener(source, event, data)

        if source == "pose_to_mirror" and event == "mirrored_data":
            self.data = data
            self.data = {
                "left_hand_pose": self.data["left_hand_pose"],
                "right_hand_pose": self.data["right_hand_pose"]
            }
            self.server.send_data(self.name, self.data)
