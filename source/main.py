import sys
import re

import euphoria as eu

from botbot import BotBot
from euphutils import EuphUtils

room_name = 'testing'
password = None
nickname = 'BotBot'

help_text = ""
with open("data/help.txt") as f:
    help_text = f.read()

short_help_text = ""
with open("data/shorthelp.txt") as f:
    short_help_text = f.read()

def main():
    botbot = BotBot(room_name, password, nickname, help_text, short_help_text)
    eu.executable.start(botbot)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            if len(sys.argv) > 3:
                print('Usage: python3 ' + sys.argv[0] + ' <room name> (default room: ' + room_name + ') <room password>')
                sys.exit(1)
            password = sys.argv[2]
        room_name = sys.argv[1]
    main()
