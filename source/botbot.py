#Standard library modules
import sys

import re
import traceback

#Additional modules
import euphoria as eu
from euphutils import EuphUtils

#Project modules
import logger
import agentid_room
from botcollection import BotCollection as bots
from snapshot import Snapshot

log = logger.Logger()

class BotBot(eu.ping_room.PingRoom, eu.chat_room.ChatRoom, agentid_room.AgentIdRoom):
    def __init__(self, room_name, password, nickname, help_text=""):
        super().__init__(room_name, password)

        self.room_name = room_name.lower()
        self.nickname = nickname
        self.password = password

        self.help_text = help_text

        bots.botbot = self

    def ready(self):
        super().ready()
        self.send_chat('/me Hello, world!')
        if Snapshot.is_enabled():
            messages = Snapshot.load('latest')[1]
            for message in messages:
                self.send_chat(message, msg_id)

    def handle_chat(self, message):
        if bots.is_bot(message['sender']['id']):
            return
        if message['content'].startswith('!'):
            command = message['content'][1:]
            sender = message['sender']['name']
            msg_id = message['id']
            # !ping
            match = EuphUtils.command('ping').match(command)
            if match:
                self.send_chat('Pong!', msg_id)
                return
            # !list @BotBot
            match = EuphUtils.command('list', self.nickname).match(command)
            if match:
                self.send_chat('Currently running bots created with ' + EuphUtils.mention(self.nickname) + ':\n' + bots.get_description(), msg_id)
                return
            # !help @BotBot
            match = EuphUtils.command('help', self.nickname).match(command)
            if match:
                self.send_chat(self.help_text, msg_id)
                return
            # !killall @BotBot
            match = EuphUtils.command('killall', self.nickname).match(command)
            if match:
                self.send_chat('Killing all bots...', msg_id)
                bots.killall()
                return
            # !createbot
            match = EuphUtils.command('createbot').match(command)
            if match:
                match = re.match(r'(?:&(\S+)\s+)?@(\S{1,36})\S*\s*(.*)', match.group(1), re.DOTALL)
                if match:
                    try:
                        bots.create(match.group(2), match.group(1).lower() if match.group(1) else self.room_name, None if match.group(1) else self.password, sender, match.group(3))
                        self.send_chat('Created ' + EuphUtils.mention(match.group(2)) + ((' in &' + match.group(1).lower()) if match.group(1) else '') + '.', msg_id)
                    except:
                        self.send_chat('Failed to create ' + EuphUtils.mention(match.group(2)) + ((' in &' + match.group(1).lower()) if match.group(1) else '') + '. Is your code valid?', msg_id)
                        self.send_chat('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), msg_id)
                else:
                    self.send_chat('It looks like you are trying to create a bot. Please make sure that you use the syntax described in ' + EuphUtils.mention(self.nickname) + '\'s help text, which can be viewed by sending the command "!help ' + EuphUtils.mention(self.nickname) + '".', msg_id)
                return
            match = EuphUtils.command('sendbot').match(command)
            if match:
                match = re.match(r'(?:&(\S+)\s+)?@(\S{1,36})\S*', match.group(1), re.DOTALL)
                if match:
                    self.send_chat('Not implemented yet', msg_id)
                else:
                    self.send_chat('It looks like you are trying to send a bot. Please make sure that you use the syntax described in ' + EuphUtils.mention(self.nickname) + '\'s help text, which can be viewed by sending the command "!help ' + EuphUtils.mention(self.nickname) + '".', msg_id)
                return
            match = EuphUtils.command('save', self.nickname).match(command)
            if match:
                messages = Snapshot.create()[1]
                for message in messages:
                    self.send_chat(message, msg_id)
                return
            match = EuphUtils.command('load', self.nickname).match(command)
            if match:
                match = re.match(r'([^\s\\/]+\.json\b|latest)', match.group(1), re.IGNORECASE)
                if match:
                    if not Snapshot.is_enabled():
                        self.send_chat('Snapshots are not enabled.', msg_id)
                        return
                    self.send_chat('A snapshot will be created so that the current state can be restored if necessary.', msg_id)
                    backup_snapshot, messages = Snapshot.create()
                    for message in messages:
                        self.send_chat(message, msg_id)
                    self.send_chat('Killing all bots...', msg_id)
                    bots.killall(False)
                    success, messages = Snapshot.load(match.group(0))
                    for message in messages:
                        self.send_chat(message, msg_id)
                    if backup_snapshot and not success:
                        self.send_chat('Reverting to snapshot created just now...', msg_id)
                        messages = Snapshot.load(backup_snapshot)[1]
                        for message in messages:
                            self.send_chat(message, msg_id)
                else:
                    self.send_chat('Please provide a valid filename.', msg_id)
                return
            match = EuphUtils.command('restart', self.nickname).match(command)
            if match:
                messages = Snapshot.create()[1]
                for message in messages:
                    self.send_chat(message, msg_id)
                self.send_chat('Killing all bots...', msg_id)
                bots.killall(False)
                self.send_chat('/me is restarting...', msg_id)
                self.quit()
