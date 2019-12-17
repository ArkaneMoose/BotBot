from .snapshot import Snapshot
from . import euphutils
from . import agentid_room
from . import longmessage_room
import euphoria as eu

import time
import re
import uuid as uuid_module
import errno
import os
import traceback

spam_threshold_messages = 10
spam_threshold_time = 5

class BotBotBot(eu.ping_room.PingRoom, eu.chat_room.ChatRoom, eu.nick_room.NickRoom, agentid_room.AgentIdRoom, longmessage_room.LongMessageRoom):
    def __init__(self, room_name, password, nickname, creator, code_struct, bots, paused=False, pause_text='', uuid=None, variables=None, initialized=False):
        super().__init__(room_name, password)

        self.bots = bots

        # Bot data
        self.code_struct = code_struct

        # Bot info
        self.uuid = uuid or str(uuid_module.uuid4())
        self.filename = os.path.join(Snapshot.snapshot_dir, 'current', self.uuid + '.json')
        self.agent_id = None
        self.room_name = room_name
        self.password = password
        self.nickname = nickname
        self.creator = creator
        self.help_text = euphutils.mention(self.nickname) + ' is a bot created by "' + creator + '"' + (' using ' + euphutils.mention(bots.botbot.nickname) if self.bots.botbot else '') + '.\n\n@' + self.nickname + ' responds to !ping, !help @' + self.nickname + ', and the following regexes:\n' + ('\n'.join(self.code_struct.get_regexes()) if len(self.code_struct.get_regexes()) > 0 else '(None)') + '\n\nTo pause this bot, use the command "!pause ' + euphutils.mention(self.nickname) + '".\nTo kill this bot, use the command "!kill ' + euphutils.mention(self.nickname) + '".\nThis bot has UUID ' + self.uuid + '.'

        # Bot state
        self.paused = paused
        self.start_time = time.time()
        self.last_times = set()
        self.variables = variables or {}
        self.code_struct.variables = self.variables
        self.initialized = initialized

        # Bot state info
        self.pause_text = pause_text
        self.generic_pause_text = 'To restore this bot, type "!restore ' + euphutils.mention(self.nickname) + '", or to kill this bot, type "!kill ' + euphutils.mention(self.nickname) + '".'

        self.write_to_file()

    def ready(self):
        super().ready()
        if not self.initialized:
            self.initialized = True
            self.send_user_messages(init=True)
            self.write_to_file()

    def write_to_file(self):
        if Snapshot.is_enabled():
            try:
                os.makedirs(os.path.join(Snapshot.snapshot_dir, 'current'))
            except OSError as err:
                if err.errno != errno.EEXIST or not os.path.isdir(Snapshot.snapshot_dir):
                    traceback.print_exc()
            try:
                with open(self.filename, 'w') as f:
                    f.write(Snapshot.pack_bot(self))
                return True
            except OSError:
                traceback.print_exc()
        return False

    def handle_chat(self, message):
        if message.get('truncated'):
            return
        if message['sender']['id'] == self.agent_id:
            return
        if self.bots.botbot and message['sender']['id'] == self.bots.botbot.agent_id:
            return

        if 'parent' in message:
            self.recv_message(message['content'], message['parent'], message['id'], message['sender']['name'], message['sender']['id'], message['time'], self.room_name)
        else:
            self.recv_message(message['content'], None, message['id'], message['sender']['name'], message['sender']['id'], message['time'], self.room_name)

    def pause(self, pause_text=None, set_pause_text=True, reply_to=None):
        changed = False
        if not self.paused:
            self.paused = True
            changed = True
        if set_pause_text and pause_text and self.pause_text != pause_text:
            self.pause_text = pause_text
            changed = True
        elif not pause_text:
            # pause_text will be sent as a message later, so load the pause_text
            # from the instance variable
            pause_text = self.pause_text
        if changed:
            self.write_to_file()
        self.send_chat(pause_text, reply_to)
        self.send_chat(self.generic_pause_text, reply_to)

    def restore(self, reply_to=None):
        changed = False
        if self.paused:
            self.paused = False
            changed = True
        if self.pause_text != '':
            self.pause_text = ''
            changed = True
        self.start_time = time.time()
        self.send_chat('/me is now restored.', reply_to)
        if changed:
            self.write_to_file()

    def set_variable(self, name, value):
        if name not in self.variables or self.variables[name] != value:
            self.variables[name] = value
            self.write_to_file()

    def del_variable(self, name):
        if name in self.variables:
            del self.variables[name]
            self.write_to_file()

    def reset_variables(self, keep={}):
        changed = False
        for key in list(self.variables.keys()):
            if key not in keep:
                del self.variables[key]
                changed = True
        if changed:
            self.write_to_file()

    def recv_message(self, content='', parent=None, this_message=None, sender='', sender_agent_id='', send_time=0, room_name=''):
        if euphutils.command('!kill', self.nickname).match(content):
            if self.bots.is_bot(sender_agent_id):
                return
            self.kill(msg_id=this_message)
        elif euphutils.command('!ukill', self.uuid).match(content):
            if self.bots.is_bot(sender_agent_id):
                return
            self.kill(msg_id=this_message)
        elif self.paused and euphutils.command('!restore', self.nickname).match(content):
            if self.bots.is_bot(sender_agent_id):
                return
            self.restore(this_message)
        elif euphutils.command('!pause', self.nickname).match(content):
            if self.bots.is_bot(sender_agent_id):
                return
            if self.paused:
                self.pause(pause_text='/me is already paused.', set_pause_text=False, reply_to=this_message)
            else:
                self.pause(pause_text='/me has been paused by "' + sender + '".', reply_to=this_message)
        elif self.paused and euphutils.command('!help', self.nickname).match(content):
            self.pause(reply_to=this_message)
        elif euphutils.command('!antighost').match(content):
            #just reset the nick to the same thing it already is
            self.change_nick(self.nickname)
        elif not self.send_user_messages(content, parent, this_message, sender, sender_agent_id, send_time, room_name) and content.startswith('!'):
            if euphutils.command('ping', '').match(content[1:]):
                self.send_chat('Pong!', this_message)
            elif euphutils.command('ping', self.nickname).match(content[1:]):
                self.send_chat('Pong!', this_message)
            elif euphutils.command('help', self.nickname).match(content[1:]):
                self.send_chat(self.help_text, this_message)
            elif euphutils.command('uuid', self.nickname).match(content[1:]):
                self.send_chat('This bot has UUID {0}.'.format(self.uuid), this_message)
            elif euphutils.command('uptime', self.nickname).match(content[1:]):
                if not self.paused:
                    self.send_chat(euphutils.uptime_str(self.start_time), this_message)
                else:
                    self.send_chat('/me is paused, so it currently has no uptime.', this_message)

    # implements only user-programmed messages and not BotBot built-in commands
    # returns True if the user programmed a response for this message
    def send_user_messages(self, content='', parent=None, this_message=None, sender='', sender_agent_id='', send_time=0, room_name='', init=False):
        default_variables = {
            'sender': sender,
            '@sender': euphutils.mention(sender),
            'atsender': euphutils.mention(sender),
            'self': self.nickname,
            '@self': euphutils.mention(self.nickname),
            'atself': euphutils.mention(self.nickname),
            'creator': self.creator,
            '@creator': euphutils.mention(self.creator),
            'atcreator': euphutils.mention(self.creator),
            'room': room_name,
            'uptimeutc': euphutils.uptime_utc(self.start_time),
            'uptime': euphutils.uptime_dhms(self.start_time),
            'uuid': self.uuid,
            'variables': None,
            'groups': None
        }
        self.variables.update(default_variables)
        if not self.paused:
            if init:
                messages = self.code_struct.get_init_messages()
            else:
                messages = self.code_struct.get_messages(content, sender)
        else:
            messages = []
        current_time = time.time()
        message = None
        for message in messages:
            for i, j in self.variables.items():
                message = message.replace('(' + i + ')', str(j))
            if len(message) == 0:
                continue
            if euphutils.command('!ping', '').match(message):
                continue
            match = re.match(r'!to\s+@(\S+)(?:\s+&(\S+))?\s+(.*)', message, re.IGNORECASE + re.DOTALL)
            if match:
                if self.spam_check(current_time, this_message):
                    self.bots.interbot(match.group(1), match.group(2).lower() if match.group(2) else None, match.group(3), sender, sender_agent_id, send_time, room_name)
                else: break
                continue
            match = re.match(r'!nick\s+(.*)', message, re.IGNORECASE + re.DOTALL)
            if match:
                new_nickname = match.group(1)
                # I run the spam check here to ensure that the bot isn't
                # spamming nick commands to the server.
                if self.spam_check(current_time, this_message):
                    self.change_nick(new_nickname)
                    self.variables.update({
                        'self': new_nickname,
                        '@self': euphutils.mention(new_nickname),
                        }) # Questionable, since there's no guarantee that
                           # the nick change succeeded, but in my opinion,
                           # the case where the nick change fails is an edge
                           # case, and this will behave as expected 99% of
                           # the time.
                else: break
                continue
            match = re.match(r'!var\s+(\S+)(?:\s+=)?\s+(.*)', message, re.IGNORECASE + re.DOTALL)
            if match:
                name = match.group(1)
                value = match.group(2)
                if name not in default_variables:
                    self.set_variable(name, value)
                continue
            match = re.match(r'!delvar\s+(\S+)', message, re.IGNORECASE + re.DOTALL)
            if match:
                name = match.group(1)
                if name not in default_variables:
                    self.del_variable(name)
                continue
            match = re.match(r'!resetvars\b', message, re.IGNORECASE + re.DOTALL)
            if match:
                self.reset_variables(keep=default_variables)
                continue
            match = re.match(r'!inline\s+(.*)', message, re.IGNORECASE + re.DOTALL)
            if match:
                if self.spam_check(current_time, this_message):
                    self.send_chat(match.group(1), parent or this_message)
                else: break
                continue
            match = re.match(r'!break\b', message, re.IGNORECASE + re.DOTALL)
            if match:
                break
            if self.spam_check(current_time, this_message):
                self.send_chat(message, this_message)
            else: break
        return message is not None

    # Before a message is sent that could be possible spam, run spam_check().
    # Returns True if the message is okay to send, or False otherwise.
    # Generally this should be used like this:
    #     if self.spam_check(current_time, this_message):
    #         self.send_chat(...)
    #     else: return
    def spam_check(self, current_time, this_message):
        self.last_times.add(current_time)
        while len(self.last_times) > spam_threshold_messages:
            self.last_times.remove(min(self.last_times))
        if not self.paused and len(self.last_times) == spam_threshold_messages:
            if max(self.last_times) - min(self.last_times) <= spam_threshold_time:
                # Spam detected!
                self.pause(pause_text='/me has been temporarily halted due to a possible spam attack being generated by this bot.', reply_to=this_message)
                return False
        while len(self.last_times) > spam_threshold_messages - 1:
            self.last_times.remove(min(self.last_times))
        return True

    def handle_nickreply(self, data):
        previous_nickname = self.nickname
        super().handle_nickreply(data)
        if self.nickname != previous_nickname:
            self.write_to_file()

    def kill(self, announce=True, msg_id=None, delete_file=True):
        if announce:
            self.send_chat('/me is now exiting.', msg_id)
        self.bots.remove(self)
        if delete_file and Snapshot.is_enabled():
            try:
                os.unlink(self.filename)
            except OSError:
                traceback.print_exc()
        self.quit()
