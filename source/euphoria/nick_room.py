from . import connection as cn

from . import room

class NickRoom(room.Room):
    """
    A nick room allows a user to quickly change names.
    """

    def __init__(self, roomname, password=None):
        super().__init__(roomname, password)

    def change_nick(self, nick):
        """
        change_nick(nick) -> None

        Change your username to a different one.
        """

        self.connection.send_packet(cn.PTYPE["COMMAND"]["NICK"], 
                                    cn.build_json(name=nick),
                                    self.handle_nickreply)
        
    def handle_nickreply(self, data):
        """
        handle_nickreply(data) -> None
        
        Handle a callback so that the nickname is only changed once you have
        received confirmation from the server.
        """
        
        self.nickname = data["data"]["to"]