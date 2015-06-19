from . import connection as cn
from . import executable

import time

class Room(executable.Executable):
    """
    A base room object that simply holds a connection and simple methods for
    interfacing with the room.
    """

    def __init__(self, roomname, password=None):
        self.connection = cn.Connection()

        self.roomname = roomname
        self.password = password
    
        self.nickname = None

    def join(self):
        """
        join() -> None
        
        Connects to the room and sends the passcode.
        """
        
        if self.connection is not None:
            self.connection.connect(self.roomname)
            
            if self.password is not None:
                self.connection.send_packet(cn.PTYPE["COMMAND"]["AUTH"],
                                            cn.build_json(passcode=self.password))

    def identify(self):
        """
        identify() -> None

        Identifies with the server according to the nickname.
        """

        if self.connection is not None:
            if self.nickname is not None:
                self.connection.send_packet(cn.PTYPE["COMMAND"]["NICK"],
                                            cn.build_json(name=self.nickname))

    def ready(self):
        """
        ready() -> None
        
        Do last minute setup for the room.
        """
        
        pass
            
    def quit(self):
        """
        quit() -> None
        
        Performs neccessary cleanup.
        """

        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def run(self):
        """
        run() -> None

        Run the room.
        """
        
        first = True
        attempts = 0
        
        while self.connection is not None:
            #Check for multiple failures in a row
            if attempts >= 2:
                self.quit()
                break
            
            #Check if quit
            if self.connection is None:
                break
            
            #Receive data and handle connection errors
            try:
                if self.connection.receive_data():
                    attempts = 0
                else:
                    #No connection initialized
                    if first:
                        first = False
                    else:
                        time.sleep(5)
                        attempts += 1

                    self.join()
                    self.identify()
                    self.ready()
            except OSError:  #Catching some exception that occurs in single threading bots
                break