import sys
import re
import json

import euphoria as eu

from botbot.botbot import BotBot
from botbot.euphutils import EuphUtils
from botbot.snapshot import Snapshot

room_name = 'testing'
password = None
nickname = 'BotBot'

help_text = '''@BotBot is a bot for Euphoria created by @myhandsaretypingwords that creates
other bots.

Usage
================================================================================
Create a bot with @BotName with some code.
    !createbot @BotName CODE
Same as the previous but specify the room to put the bot in.
    !createbot &room @BotName CODE
List all the bots that are currently running and have been created by @BotBot.
    !list @BotBot
Send a bot with the name @BotName to the specified room.
    !sendbot &room @BotName
Kill a bot with the name @BotName.
    !kill @BotName
Pause a bot with the name @BotName.
    !pause @BotName
Kill all the bots created by @BotBot.
    !killall @BotName
Take a snapshot of the state of @BotBot.
    !save @BotBot
Load the latest snapshot.
    !load @BotBot latest
Load a snapshot with a specific file name.
    !load @BotBot FILENAME
Restart @BotBot.
    !restart @BotBot

More Info
================================================================================
View the @BotBot wiki at https://github.com/ArkaneMoose/BotBot/wiki for a
comprehensive guide on how to use @BotBot, including a guide on how to write
@BotBot code and a list of features and restrictions that bots created with
@BotBot have.

Good luck!
================================================================================
Good luck on your journey to becoming a bot programmer.

If you need help, you can ask @myhandsaretypingwords, @nihizg, or any of the
other awesome Euphorians in &programming for help with any bot-related questions.

Have fun, and please be respectful!

@BotBot is open-source! Feel free to view the code, contribute, and report
issues at https://github.com/ArkaneMoose/BotBot.

@BotBot complies with the Euphorian bot standards.'''

short_help_text = '''@BotBot is a bot for Euphoria created by @myhandsaretypingwords that creates
other bots. Type "!help @BotBot" to learn more.'''

def main():
    botbot = BotBot(room_name, password, nickname, help_text, short_help_text)
    eu.executable.start(botbot)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) > 2 or sys.argv[1].lower() == '--help':
            print('Usage: python3 -m botbot <path to config.json>')
            sys.exit(1)
        with open(sys.argv[1]) as f:
            config = json.load(f)
        room_name = config.get('room', room_name)
        password = config.get('password', password)
        nickname = config.get('nickname', nickname)
        help_text = config.get('helpText', help_text.replace('@BotBot', EuphUtils.mention(nickname)))
        short_help_text = config.get('shortHelpText', short_help_text.replace('@BotBot', EuphUtils.mention(nickname)))
        Snapshot.snapshot_dir = config.get('snapshotDirectory', Snapshot.snapshot_dir)
    main()
