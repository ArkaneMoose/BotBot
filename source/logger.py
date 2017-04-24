import sys
import datetime

class Logger:
    def __init__(self, filename="console"):
        self.file = None
        self.logging = True

        if filename is None:
            self.logging = False
        else:
            if filename != "console":
                self.file = open(filename, 'w')

    def __del__(self):
        if self.file is not None:
            self.file.close()

    def write(self, message):
        if self.logging:
            l = '[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] ' + message
            if self.file is None:
                sys.stderr.write(l + '\n')
                sys.stderr.flush()
            else:
                self.file.write(l + '\n')
                self.file.flush()
