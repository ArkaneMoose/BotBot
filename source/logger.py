import sys
import datetime

class Logger:
    def __init__(self, filename=None):
        self.file = None
        if filename is not None:
            self.file = open(filename, 'w')

    def __del__(self):
        if self.file is not None:
            self.file.close()

    def log(self, message):
        l = '[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] ' + message
        if self.file is None:
            print(l)
        else:
            self.file.write(l + '\n')
