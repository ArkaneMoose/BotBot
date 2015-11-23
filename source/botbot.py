#Standard library modules
import sys
import threading

import re
import time
import datetime
import traceback

#Additional modules
import euphoria as eu
from botbot.euphutils import EuphUtils

#Project modules
import botbot.logger as logger
import botbot.agentid_room as agentid_room
import botbot.longmessage_room as longmessage_room
from botbot.botcollection import BotCollection
from botbot.snapshot import Snapshot

log = logger.Logger()

class BotBot(eu.ping_room.PingRoom, eu.chat_room.ChatRoom, agentid_room.AgentIdRoom, longmessage_room.LongMessageRoom):
    def __init__(self, room_name, password, nickname, help_text="", short_help_text=""):
        super().__init__(room_name, password)

        self.room_name = room_name.lower()
        self.nickname = nickname
        self.password = password

        self.help_text = help_text
        self.short_help_text = short_help_text

        self.start_time = time.time()

        self.bots = BotCollection(self)
        self.botthread = threading.Thread(target=self.bots.run)

        self.initialized = False

    def init(self):
        log.write(EuphUtils.mention(self.nickname) + ' has started.')

        self.send_chat('Hello, world!')
        if Snapshot.is_enabled():
            messages = Snapshot.load_current(self.bots)
            for message in messages:
                self.send_chat(message)
        else:
            self.send_chat('Snapshots are not enabled.')

    def ready(self):
        super().ready()
        if not self.initialized:
            self.initialized = True
            self.init()

    def run(self):
        self.botthread.start()
        super().run()

    def handle_chat(self, message):
        if message.get('truncated'):
            return
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
            # !uptime @BotBot
            match = EuphUtils.command('uptime', self.nickname).match(command)
            if match:
                self.send_chat(EuphUtils.uptime_str(self.start_time), msg_id)
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
                match = re.match(r'(?:&(\S+)\s+)?@(\S{1,36})\S*(?:\s+(\d+))?', match.group(1), re.DOTALL)
                if match:
                    destination_room = match.group(1)
                    desired_bot = match.group(2)
                    identifier = match.group(3)
                    matching_bots = self.bots.retrieve(mention_name=desired_bot)
                    if len(matching_bots) == 0:
                        self.send_chat('Sorry, no bots named ' + EuphUtils.mention(desired_bot) + ' were found.', msg_id)
                    elif len(matching_bots) > 1 and not identifier:
                        bot_description_list = []
                        for bot in matching_bots:
                            bot_description_list.append(str(len(bot_description_list) + 1) + ': ' + self.bots.get_description(bot=bot))
                        bot_descriptions = '\n'.join(bot_description_list)
                        self.send_chat('Multiple bots named ' + EuphUtils.mention(desired_bot) + ' were found.\n' +
                        'Select the one you want by sending the command: ' +
                        '"!sendbot' + (' &' + destination_room if destination_room else '') + ' @' + desired_bot + ' [number of desired bot]"\n\n' +
                        bot_descriptions, msg_id)
                    else:
                        try:
                            matching_bot = matching_bots[(int(identifier) - 1) if identifier else 0]
                            try:
                                self.bots.create(matching_bot.nickname, destination_room.lower() if destination_room else self.room_name, None if destination_room else self.password, matching_bot.creator, matching_bot.code_struct.parse_string)
                                self.send_chat('Created ' + EuphUtils.mention(matching_bot.nickname) + ((' in &' + destination_room.lower()) if destination_room else '') + '.', msg_id)
                            except:
                                self.send_chat('Failed to create ' + EuphUtils.mention(matching_bot.nickname) + ((' in &' + destination_room.lower()) if destination_room else '') + '.', msg_id)
                                self.send_chat('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), msg_id)
                        except ValueError:
                            self.send_chat('Unable to parse number of the desired bot.', msg_id)
                        except IndexError:
                            bot_description_list = []
                            for bot in matching_bots:
                                bot_description_list.append(str(len(bot_description_list) + 1) + ': ' + self.bots.get_description(bot=bot))
                            bot_descriptions = '\n'.join(bot_description_list)
                            self.send_chat('The number of desired bot is out of range.\n' +
                            'Select the bot you want by sending the command: ' +
                            '"!sendbot' + (' &' + destination_room if destination_room else '') + ' @' + desired_bot + ' [number of desired bot]"\n\n' +
                            bot_descriptions, msg_id)
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
                if not Snapshot.is_enabled():
                    self.send_chat('Snapshots are not enabled.', msg_id)
                    return
                match = re.match(r'([^\s\\/]+\.tar\.gz\b|latest)', match.group(1), re.IGNORECASE)
                if match:
                    filepath = Snapshot.get_filepath(match.group(0))
                else:
                    filepath = None
                if filepath:
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
                self.send_chat('Killing all bots...', msg_id)
                self.bots.killall(announce=False, delete_file=False)
                self.send_chat('/me is restarting...', msg_id)
                self.quit()

    def quit(self):
        super().quit()
        self.bots.quit()
        self.botthread.join()
