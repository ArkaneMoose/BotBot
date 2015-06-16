import threading
import json
import time
import re

from websocket import create_connection, WebSocketConnectionClosedException

import logger

#Global vars - BAD!!!
spam_threshold_messages = 10
spam_threshold_time = 5

bots = []

class bot_thread(threading.Thread):
    def __init__(self, nickname, data, roomname, creator, log=None):
        super().__init__()

        if log is None:
            self.log = logger.Logger(filename=None)
        else:
            self.log = log

        #Bot state
        self.paused = False
        self.finished = False

        #Bot info
        self.room_name = roomname
        self.nickname = nickname
        self.creator = creator

        self.last_times = []
        self._kill = threading.Event()
        self.data = data
        self.mid = 0

        self.agent_id = None

        #Bot text
        self.help_text = '@' + self.nickname + ' is a bot created by \"' + creator + '\" using @' + nickname + '.\n\n@' + self.nickname + ' responds to !ping, !help @' + self.nickname + ', and the following regexes:\n' + '\n'.join(self.data.get_regexes()) + '\n\nTo pause this bot, use the command !pause @' + self.nickname + '.\nTo kill this bot, use the command !kill @' + self.nickname + '.'
        self.pause_text = ''

        #Connections
        self.web_socket_url = 'wss://euphoria.io/room/{}/ws'.format(self.room_name)

        self.log.write('Connecting to ' + self.web_socket_url + '...')
        self.ws = create_connection(self.web_socket_url)

        self.log.write('[' + self.nickname + '] Connected!')
        self.thread_send_nick()

    def run(self):
        while not self.is_dead():
            try:
                if self.is_dead():
                    self.ws.close()
                    return
                data = self.ws.recv()
                if self.is_dead():
                    self.ws.close()
                    return
            except WebSocketConnectionClosedException:
                if self.is_dead():
                    return
                self.log.write('[' + self.nickname + '] Disconnected. Attempting to reconnect...')
                self.ws = create_connection(web_socket_url)
                self.thread_send_nick()
                self.log.write('[' + self.nickname + '] Reconnected!')
                data = self.ws.recv()
                if self.is_dead():
                    self.ws.close()
                    return
            data = json.loads(data)
            if data['type'] == 'ping-event':
                self.thread_send_ping()
            if data['type'] == 'nick-reply':
                self.agent_id = data['data']['id']
            if data['type'] == 'send-event':
                content = data['data']['content']
                parent = data['data']['parent']
                this_message = data['data']['id']
                sender = data['data']['sender']['name']
                send_time = data['data']['time']
                sender_agent_id = data['data']['sender']['id']
                self.recv_message(content, parent, this_message, sender, send_time, sender_agent_id, self.room_name)
        self.finished = True

    def recv_message(self, content='', parent=None, this_message=None, sender='', send_time=0, sender_agent_id='', room_name=''):
        if sender_agent_id == self.agent_id:
            return
        if (len(content) == 7 + len(self.nickname) or (len(content) >= 7 + len(self.nickname) and content[7+len(self.nickname)] == ' ')) and content[0:7+len(self.nickname)].lower() == ('!kill @' + self.nickname).lower():
            for bot in bots:
                if sender_agent_id == bot.agent_id:
                    return
            self.thread_send_message('/me is now exiting.', this_message)
            self.kill()
        elif self.paused and ((len(content) == 10 + len(self.nickname) or (len(content) >= 10 + len(self.nickname) and content[10+len(self.nickname)] == ' ')) and content[0:10+len(self.nickname)].lower() == ('!restore @' + self.nickname).lower()):
            for bot in bots:
                if sender_agent_id == bot.agent_id:
                    return
            self.thread_send_message('/me is now restored.', this_message)
            self.paused = False
            self.pause_text = ''
        elif (len(content) == 8 + len(self.nickname) or (len(content) >= 8 + len(self.nickname) and content[8+len(self.nickname)] == ' ')) and content[0:8+len(self.nickname)].lower() == ('!pause @' + self.nickname).lower():
            for bot in bots:
                if sender_agent_id == bot.agent_id:
                    return
            if self.paused:
                self.thread_send_message('/me is already paused.', this_message)
                self.thread_send_message('To restore this bot, type \"!restore @' + self.nickname + '\", or to kill this bot, type \"!kill @' + self.nickname + '\".', this_message)
            else:
                self.paused = True
                self.pause_text = '/me has been paused by \"' + sender + '\".'
                self.thread_send_message(self.pause_text, this_message)
                self.thread_send_message('To restore this bot, type \"!restore @' + self.nickname + '\", or to kill this bot, type \"!kill @' + self.nickname + '\".', this_message)
        elif self.paused and ((len(content) == 7 + len(self.nickname) or (len(content) >= 7 + len(self.nickname) and content[7+len(self.nickname)] == ' ')) and content[0:7+len(self.nickname)].lower() == ('!help @' + self.nickname).lower()):
            self.thread_send_message(self.pause_text, this_message)
            self.thread_send_message('To restore this bot, type \"!restore @' + self.nickname + '\", or to kill this bot, type \"!kill @' + self.nickname + '\".', this_message)
        elif self.paused:
            return
        elif len(self.data.get_messages(content, sender)) > 0:
            self.last_times.append(time.time())
            while len(self.last_times) > spam_threshold_messages:
                del self.last_times[0]
            if not self.paused and len(self.last_times) == spam_threshold_messages:
                if self.last_times[-1] - self.last_times[0] <= spam_threshold_time:
                    #Spam detected!
                    self.paused = True
                    self.pause_text = '/me has been temporarily halted due to a possible spam attack being generated by this bot.'
                    self.thread_send_message(self.pause_text)
                    self.thread_send_message('To restore this bot, type \"!restore @' + self.nickname + '\", or to kill this bot, type \"!kill @' + self.nickname + '\".')
                    return
            while len(self.last_times) > spam_threshold_messages - 1:
                del self.last_times[0]
            for x in self.data.get_messages(content, sender):
                message = x.replace('(sender)', sender).replace('(@sender)', '@' + sender.replace(' ', '')).replace('(room)', room_name)
                if re.match('^!ping\\b', message, re.IGNORECASE):
                    continue
                match = re.match('!to\\s+@(\\S+)\\s+&(\\S+)\\s+([\\s\\S]*)', message, re.IGNORECASE)
                if match:
                    for bot in bots:
                        if bot.nickname.lower() == match.group(1).lower() and bot.room_name.lower() == match.group(2).lower():
                            bot.recv_message(match.group(3), None, None, sender, send_time, sender_agent_id, room_name)
                    continue
                match = re.match('!to\\s+@(\\S+)\\s+([\\s\\S]*)', message, re.IGNORECASE)
                if match:
                    for bot in bots:
                        if bot.nickname.lower() == match.group(1).lower():
                            bot.recv_message(match.group(2), None, None, sender, send_time, sender_agent_id, room_name)
                    continue
                self.thread_send_message(message, this_message)
        elif len(content) > 0 and content[0] == '!':
            if len(content) >= 5 and content[1:5].lower() == 'ping':
                self.thread_send_message('Pong!', this_message)
                self.log.write('[' + self.nickname + '] Ponged to a ping from \"' + sender + '\".')
            elif (len(content) == 7 + len(self.nickname) or (len(content) >= 7 + len(self.nickname) and content[7+len(self.nickname)] == ' ')) and content[1:7+len(self.nickname)].lower() == ('help @' + self.nickname).lower():
                self.thread_send_message(self.help_text, this_message)
                self.log.write('[' + self.nickname + '] Sent help text to \"' + sender + '\".')

    def thread_send(self, message):
        try:
            self.ws.send(message)
        except WebSocketConnectionClosedException:
            self.ws = create_connection(self.web_socket_url)
            self.ws.send(message)

    def thread_send_ping(self):
        reply = {'type':'ping-reply','data':{'time':int(time.time())},'id':str(self.mid)}
        reply = json.dumps(reply)
        self.thread_send(reply)
        self.mid += 1

    def thread_send_message(self, message, parent=None):
        message = {'type':'send','data':{'content':message,'parent':parent},'id':str(self.mid)}
        message = json.dumps(message)
        self.thread_send(message)
        self.mid += 1

    def thread_send_nick(self, nick=None):
        if nick == None:
            nick = self.nickname
        message = {'type':'nick','data':{'name':nick},'id':str(self.mid)}
        message = json.dumps(message)
        self.thread_send(message)
        self.mid += 1

    def kill(self):
        self._kill.set()
        self.ws.close()
        try:
            bots.remove(self)
        except ValueError:
            pass
        self.log.write('[' + self.nickname + '] Exiting.')

    def announce_and_kill(self, parent=None):
        try:
            self.thread_send_message('/me is now exiting.', parent)
        except WebSocketConnectionClosedException:
            pass
        self.kill()

    def is_dead(self):
        return self._kill.isSet()
