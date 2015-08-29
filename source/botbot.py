#Standard library modules
import sys
import threading

import re
import traceback

#Additional modules
import euphoria as eu
from euphutils import EuphUtils

#Project modules
import logger
import agentid_room
from botcollection import BotCollection
from snapshot import Snapshot

log = logger.Logger()

class BotBot(eu.ping_room.PingRoom, eu.chat_room.ChatRoom, agentid_room.AgentIdRoom):
    def __init__(self, room_name, password, nickname, help_text="", short_help_text=""):
        super().__init__(room_name, password)

        self.room_name = room_name.lower()
        self.nickname = nickname
        self.password = password

        self.help_text = help_text
        self.short_help_text = short_help_text

        self.bots = BotCollection(self)
        self.botthread = threading.Thread(target=self.bots.run)

    def ready(self):
        super().ready()

        self.send_chat('Hello, world!')
        if Snapshot.is_enabled():
            filepath = Snapshot.get_filepath('latest')
            if filepath:
                messages = Snapshot.load(filepath, self.bots)
                for message in messages:
                    self.send_chat(message)
            else:
                self.send_chat('Could not find snapshot.')
        else:
            self.send_chat('Snapshots are not enabled.')

    def run(self):
        self.botthread.start()
        super().run()

    def handle_chat(self, message):
        if self.bots.is_bot(message['sender']['id']):
            return
        if message['content'].startswith('!'):
            command = message['content'][1:]
            sender = message['sender']['name']
            msg_id = message['id']
            # !ping
            match = EuphUtils.command('ping', '').match(command)
            if match:
                self.send_chat('Pong!', msg_id)
                return
            # !ping @BotBot
            match = EuphUtils.command('ping', self.nickname).match(command)
            if match:
                self.send_chat('Pong!', msg_id)
                return
            # !list @BotBot
            match = EuphUtils.command('list', self.nickname).match(command)
            if match:
                self.send_chat('Currently running bots created with ' + EuphUtils.mention(self.nickname) + ':\n' + self.bots.get_description(), msg_id)
                return
            # !help
            match = EuphUtils.command('help', '').match(command)
            if match:
                self.send_chat(self.short_help_text, msg_id)
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
                self.bots.killall()
                return
            # !createbot
            match = EuphUtils.command('createbot').match(command)
            if match:
                match = re.match(r'(?:&(\S+)\s+)?@(\S{1,36})\S*\s*(.*)', match.group(1), re.DOTALL)
                if match:
                    try:
                        self.bots.create(match.group(2), match.group(1).lower() if match.group(1) else self.room_name, None if match.group(1) else self.password, sender, match.group(3))
                        self.send_chat('Created ' + EuphUtils.mention(match.group(2)) + ((' in &' + match.group(1).lower()) if match.group(1) else '') + '.', msg_id)
                    except:
                        self.send_chat('Failed to create ' + EuphUtils.mention(match.group(2)) + ((' in &' + match.group(1).lower()) if match.group(1) else '') + '. Is your code valid?', msg_id)
                        self.send_chat('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), msg_id)
                else:
                    self.send_chat('It looks like you are trying to create a bot. Please make sure that you use the syntax described in ' + EuphUtils.mention(self.nickname) + '\'s help text, which can be viewed by sending the command "!help ' + EuphUtils.mention(self.nickname) + '".', msg_id)
                return
            #!sendbot
            match = EuphUtils.command('sendbot').match(command)
            if match:
                match = re.match(r'(?:&(\S+)\s+)?@(\S{1,36})\S*', match.group(1), re.DOTALL)
                if match:
                    self.send_chat('Not implemented yet', msg_id)
                else:
                    self.send_chat('It looks like you are trying to send a bot. Please make sure that you use the syntax described in ' + EuphUtils.mention(self.nickname) + '\'s help text, which can be viewed by sending the command "!help ' + EuphUtils.mention(self.nickname) + '".', msg_id)
                return
            #!save
            match = EuphUtils.command('save', self.nickname).match(command)
            if match:
                messages = Snapshot.create(self.bots)
                for message in messages:
                    self.send_chat(message, msg_id)
                return
            #!load
            match = EuphUtils.command('load', self.nickname).match(command)
            if match:
                match = re.match(r'([^\s\\/]+\.json\b|latest)', match.group(1), re.IGNORECASE)
                if match:
                    filepath = Snapshot.get_filepath(match.group(0))
                else:
                    filepath = None
                if filepath:
                    if not Snapshot.is_enabled():
                        self.send_chat('Snapshots are not enabled.', msg_id)
                        return
                    self.send_chat('A snapshot will be created so that the current state can be restored if necessary.', msg_id)
                    messages = Snapshot.create(self.bots)
                    for message in messages:
                        self.send_chat(message, msg_id)
                    self.send_chat('Killing all bots...', msg_id)
                    self.bots.killall(False)

                    messages = Snapshot.load(filepath, self.bots)
                    for message in messages:
                        self.send_chat(message, msg_id)
                else:
                    self.send_chat('Please provide a valid filename.', msg_id)
                return
            #!restart
            match = EuphUtils.command('restart', self.nickname).match(command)
            if match:
                messages = Snapshot.create(self.bots)
                for message in messages:
                    self.send_chat(message, msg_id)
                self.send_chat('Killing all bots...', msg_id)
                self.bots.killall(False)
                self.send_chat('/me is restarting...', msg_id)
                self.quit()

    def cleanup(self):
        self.bots.quit()

        self.botthread.join()
