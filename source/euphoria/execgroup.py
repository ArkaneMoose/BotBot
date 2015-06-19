from . import executable

import threading
import time

class ExecGroup(executable.Executable):
    """
    A class that groups multiple executables together, so that they can be run
    at the same time.
    """
    
    def __init__(self):
        self.execs = []
        self.exec_threads = []
        
        self.stop = False

    def add(self, toadd):
        """
        add(toadd) -> None
        
        Add an executable to the list of things to be run.
        """
        
        self.execs.append(toadd)
        self.exec_threads.append(threading.Thread(target=toadd.run))

    def run(self):
        """
        run() -> None
        
        Start all the executables and wait in a loop.
        """
        
        for e in self.exec_threads:
            e.start()

        while not self.stop:
            time.sleep(2)

    def quit(self):
        """
        quit() -> None
        
        Quit nicely.
        """
        
        self.stop = True
        
        for i in self.execs:
            i.quit()

        for i in self.exec_threads:
            i.join()