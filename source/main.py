import sys

import euphoria as eu
from botbot import BotBot

room_name = 'testing'
password = None
nickname = 'BotBot'

def main():
    botbot = BotBot(room_name, password, nickname)
    eu.executable.start(botbot)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            if len(sys.argv) > 3:
                if len(sys.argv) > 4:
                    print('Usage: python3 ' + sys.argv[0] + ' <room name> (default room: ' + room_name + ') <nickname> (default nickname: ' + nickname + ') <room password>')
                    sys.exit(1)
                password = sys.argv[3]
            help_text = EuphUtils.mention_regex(nickname).sub(EuphUtils.mention(sys.argv[2]), help_text)
            help_text = re.sub(r'\b' + nickname + r'\b', sys.argv[2], help_text, 0, re.IGNORECASE)
            nickname = sys.argv[2]
        room_name = sys.argv[1]
    main()
