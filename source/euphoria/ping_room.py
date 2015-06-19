from . import connection as cn

from . import room

import time

class PingRoom(room.Room):
    """
    A ping room maintains a connection with the server.
    """

    def __init__(self, roomname, password=None):
        super().__init__(roomname, password)

        self.connection.add_callback(cn.PTYPE["EVENT"]["PING"],
                                        self.handle_ping)

    def handle_ping(self, packet):
        """
        handle_ping(packet) -> None

        The method sends a ping packet off to the server to maintain the
        connection.
        """

        self.connection.send_packet(cn.PTYPE["REPLY"]["PING"],
                                        cn.build_json(time=int(time.time())))