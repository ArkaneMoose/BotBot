from euphoria import connection as cn

from euphoria import room

class LongMessageRoom(room.Room):
    """
    A long message room allows your bot to automatically retrieve long messages.
    If this room is implemented, handle_chat(message) should be ignored if
    message.get('truncated') == True, as the handle_chat(message) should be
    reissued with the full message by this room.
    """

    def __init__(self, roomname, password=None, attempts=None):
        super().__init__(roomname, password, attempts)

        self.connection.add_callback("send-event", self.request_full_message)
        self.connection.add_callback("get-message-reply", self.handle_getmessagereply)

    def request_full_message(self, message):
        """
        request_full_message(message) -> None

        Checks if message is truncated; if so, issues a get-message command.
        """

        if message.get("data", {}).get("truncated"):
            self.connection.send_packet("get-message",
                cn.build_json(id=message["data"]["id"]))

    def handle_getmessagereply(self, message):
        """
        handle_getmessagereply(message) -> None

        Passes message to handle_chat().
        """

        self.handle_chat(message["data"]);

    def handle_chat(self, message):
        """
        handle_chat(message) -> None

        Override this method to handle chats.
        """

        pass
