from euphoria import connection as cn

from euphoria import room

class AgentIdRoom(room.Room):
    """
    An agent ID room keeps track of your agent ID.
    """

    def __init__(self, roomname, password=None, attempts=None):
        super().__init__(roomname, password, attempts)

        self.connection.add_callback("nick-reply", self.handle_nickreply)

        self.connection.add_callback("send-reply", self.handle_sendreply)

        self.agent_id = None

    def handle_nickreply(self, data):
        """
        handle_nickreply(data) -> None

        Update agent ID if it has changed.
        """

        try:
            if data["data"] and data["data"]["id"]:
                self.agent_id = data["data"]["id"]
        except KeyError:
            pass

    def handle_sendreply(self, data):
        """
        handle_sendreply(data) -> None

        Update agent ID if it has changed.
        """

        try:
            if data["data"] and data["data"]["sender"] and data["data"]["sender"]["id"]:
                self.agent_id = data["data"]["sender"]["id"]
        except KeyError:
            pass
