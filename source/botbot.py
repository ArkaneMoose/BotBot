from websocket import create_connection, WebSocketConnectionClosedException
import json
import time
import datetime
import sys
import os
import random
import threading
import re

def uniprint(message):
    sys.stdout.buffer.write((message + '\n').encode('utf8'))
    sys.stdout.buffer.flush()

help_text = ""
with open("data/help.txt") as f:
    help_text = f.read()

room_name = 'testing'
nickname = 'BotBot'
snapshot_dir = 'snapshots'

bots = []

spam_threshold_messages = 5
spam_threshold_time = 3

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            if len(sys.argv) > 3:
                uniprint('Usage: python3 ' + sys.argv[0] + ' <room name> (default room: ' + room_name + ') <nickname> (default nickname: ' + nickname + ')')
                sys.exit(1)
            nickname = sys.argv[2]
        room_name = sys.argv[1]

web_socket_url = 'wss://euphoria.io/room/{}/ws'.format(room_name)
uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Connecting to ' + web_socket_url + ' as ' + nickname + '...')
ws = create_connection(web_socket_url)
mid = 0
agent_id = None

class bot_data_parser:
    def __init__(self, parse_string):
        temp = ''
        self.array = []
        self.parse_string = parse_string
        regex_mode = True
        i = 0
        if parse_string[i] == '\n':
            i += 1
        while i < len(parse_string):
            if regex_mode:
                if parse_string[i:i+4] == ' -> ':
                    i += 4
                    regex_mode = False
                    self.array.append([re.compile(temp, re.IGNORECASE + re.UNICODE)])
                    temp = ''
                elif parse_string[i:i+3] == ' ->' or parse_string[i:i+3] == '-> ':
                    i += 3
                    regex_mode = False
                    self.array.append([re.compile(temp, re.IGNORECASE + re.UNICODE)])
                    temp = ''
                elif parse_string[i:i+2] == '->':
                    i += 2
                    regex_mode = False
                    self.array.append([re.compile(temp, re.IGNORECASE + re.UNICODE)])
                    temp = ''
                else:
                    temp += parse_string[i]
                    i += 1
            else:
                while i < len(parse_string) and parse_string[i] != ';':
                    temp += parse_string[i]
                    i += 1
                self.array[-1].append(self.parse_response_string(temp))
                temp = ''
                if parse_string[i:i+3] == '; \n':
                    i += 3
                elif parse_string[i:i+2] == '; ':
                    i += 2
                elif parse_string[i:i+2] == ';\n':
                    i += 2
                else:
                    i += 1
                regex_mode = True

    def load_array(self, array):
        self.array = array

    def get_messages(self, content, sender):
        messages = []
        for entry in self.array:
            search_string = content
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
                groups = match.groups('')
                i = 0
                while i < len(messages_to_add):
                    j = len(groups) - 1
                    while j >= 0:
                        messages_to_add[i] = messages_to_add[i].replace('\\' + str(j + 1), groups[j])
                        j -= 1
                    i += 1
                messages.extend(messages_to_add)
                continue
            search_string = content.replace('@' + sender.replace(' ', ''), '(@sender)')
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
                groups = match.groups('')
                i = 0
                while i < len(messages_to_add):
                    j = len(groups) - 1
                    while j >= 0:
                        messages_to_add[i] = messages_to_add[i].replace('\\' + str(j + 1), groups[j])
                        j -= 1
                    i += 1
                messages.extend(messages_to_add)
                continue
            search_string = content.replace(sender, '(sender)')
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
                groups = match.groups('')
                i = 0
                while i < len(messages_to_add):
                    j = len(groups) - 1
                    while j >= 0:
                        messages_to_add[i] = messages_to_add[i].replace('\\' + str(j + 1), groups[j])
                        j -= 1
                    i += 1
                messages.extend(messages_to_add)
                continue
            search_string = content.replace('@' + sender.replace(' ', ''), '(@sender)').replace(sender, '(sender)')
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
                groups = match.groups('')
                i = 0
                while i < len(messages_to_add):
                    j = len(groups) - 1
                    while j >= 0:
                        messages_to_add[i] = messages_to_add[i].replace('\\' + str(j + 1), groups[j])
                        j -= 1
                    i += 1
                messages.extend(messages_to_add)
                continue
        return messages

    def get_regexes(self):
        regexes = []
        for entry in self.array:
            regexes.append(entry[0].pattern)
        return regexes

    def parse_entry(self, entry):
        if entry[0] == 0:
            return [entry[1]]
        if entry[0] == 1:
            return self.parse_entry(entry[random.randint(1, len(entry) - 1)])
        if entry[0] == 2:
            retval = []
            i = 1
            while i < len(entry):
                retval.extend(self.parse_entry(entry[i]))
                i += 1
            return retval
        return []

    def parse_response_string(self, string):
        if len(string) < 2:
            return [0, string]
        if string == '<>':
            return [3]
        if string[0] == '<' and string[-1] == '>':
            try:
                int(string[1:-1])
                return [3]
            except ValueError:
                return [0, string]
        if (string[0] == '[' and string[-1] == ']') or (string[0] == '{' and string[-1] == '}'):
            temp2 = []
            temp = string[1:-1].split(',')
            if string[0] == '[':
                temp2.append(1)
            else:
                temp2.append(2)
            i = 0
            while i < len(temp):
                if len(temp[i]) > 0 and temp[i][0] == ' ':
                    temp[i] = temp[i][1:]
                if len(temp[i]) > 0 and temp[i][0] == '\n':
                    temp[i] = temp[i][1:]
                if temp[i][0] == '[' or temp[i][0] == '{':
                    j = i
                    brackets = 0
                    braces = 0
                    start_loop = True
                    while start_loop or ((brackets > 0 or braces > 0) and j < len(temp)):
                        start_loop = False
                        if len(temp[j]) == 0:
                            j += 1
                            continue
                        if temp[j][0] == '[':
                            brackets += 1
                        if temp[j][-1] == ']':
                            brackets -= 1
                        if temp[j][0] == '{':
                            braces += 1
                        if temp[j][-1] == '}':
                            braces -= 1
                        j += 1
                    temp2.append(self.parse_response_string(','.join(temp[i:j])))
                    i = j
                elif temp[i][0] == '<' and temp[i][-1] == '>':
                    if len(temp[i]) == 2:
                        temp2.append([3])
                        i += 1
                        continue
                    else:
                        try:
                            for x in range(0, int(temp[i][1:-1])):
                                temp2.append([3])
                                i += 1
                            continue
                        except ValueError:
                            temp2.append([0, temp[i]])
                            i += 1
                            continue
                else:
                    temp2.append(self.parse_response_string(temp[i]))
                    i += 1
            return temp2
        return [0, string]

class bot_thread (threading.Thread):
    def __init__(self, thread_nickname, data, thread_room_name, creator):
        threading.Thread.__init__(self)
        self.paused = False
        self.finished = False
        self.last_times = []
        self._kill = threading.Event()
        self.data = data
        self.mid = 0
        self.room_name = thread_room_name
        self.agent_id = None
        self.web_socket_url = 'wss://euphoria.io/room/{}/ws'.format(self.room_name)
        self.nickname = thread_nickname
        self.creator = creator
        self.help_text = '@' + self.nickname + ' is a bot created by \"' + creator + '\" using @' + nickname + '.\n\n@' + self.nickname + ' responds to !ping, !help @' + self.nickname + ', and the following regexes:\n' + '\n'.join(self.data.get_regexes()) + '\n\nTo pause this bot, use the command !pause @' + self.nickname + '.\nTo kill this bot, use the command !kill @' + self.nickname + '.'
        self.pause_text = ''
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] [' + self.nickname + '] Connecting to ' + self.web_socket_url + '...')
        self.ws = create_connection(self.web_socket_url)
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] [' + self.nickname + '] Connected!')
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
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] [' + self.nickname + '] Disconnected. Attempting to reconnect...')
                self.ws = create_connection(web_socket_url)
                self.thread_send_nick()
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] [' + self.nickname + '] Reconnected!')
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
        if sender_agent_id == agent_id:
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
                    ## Spam detected!
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
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] [' + self.nickname + '] Ponged to a ping from \"' + sender + '\".')
            elif (len(content) == 7 + len(self.nickname) or (len(content) >= 7 + len(self.nickname) and content[7+len(self.nickname)] == ' ')) and content[1:7+len(self.nickname)].lower() == ('help @' + self.nickname).lower():
                self.thread_send_message(self.help_text, this_message)
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] [' + self.nickname + '] Sent help text to \"' + sender + '\".')

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
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] [' + self.nickname + '] Exiting.')
    def announce_and_kill(self, parent=None):
        try:
            self.thread_send_message('/me is now exiting.', parent)
        except WebSocketConnectionClosedException:
            pass
        self.kill()
    def is_dead(self):
        return self._kill.isSet()

def send(message):
    global ws
    try:
        ws.send(message)
    except WebSocketConnectionClosedException:
        ws = create_connection(web_socket_url)
        ws.send(message)

def send_ping():
    global ws
    global mid
    reply = {'type':'ping-reply','data':{'time':int(time.time())},'id':str(mid)}
    reply = json.dumps(reply)
    send(reply)
    mid += 1

def send_message(message, parent=None):
    global mid
    global ws
    message = {'type':'send','data':{'content':message,'parent':parent},'id':str(mid)}
    message = json.dumps(message)
    send(message)
    mid += 1

def send_nick(nick=nickname):
    global mid
    global ws
    message = {'type':'nick','data':{'name':nick},'id':str(mid)}
    message = json.dumps(message)
    send(message)
    mid += 1

def create_snapshot(this_message=None, sender='(System)'):
    global bots
    try:
        new_bots = []
        packed_bots = []
        bot_names = []
        for bot in bots:
            if not bot.finished:
                new_bots.append(bot)
                packed_bots.append({'nickname': bot.nickname, 'data': bot.data.parse_string, 'room': bot.room_name, 'creator': bot.creator, 'paused': bot.paused, 'pauseText': bot.pause_text})
                if not bot.paused:
                    if bot.room_name != room_name:
                        bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ')')
                    else:
                        bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\")')
                else:
                    if bot.room_name != room_name:
                        bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ') (paused)')
                    else:
                        bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (paused)')
        bots = new_bots
        if len(packed_bots) == 0:
            send_message('There are no running bots. A snapshot will not be created.', this_message)
            return None
        formatted_datetime = datetime.datetime.now().strftime('%m-%d-%Y_%H%M%S')
        filename = formatted_datetime + '.json'
        filepath = os.path.join(snapshot_dir, filename)
        i = 1
        while os.path.isfile(filepath):
            filename = formatted_datetime + '_' + str(i) + '.json'
            filepath = os.path.join(snapshot_dir, filename)
            i += 1
        file = open(filepath, 'w')
        json.dump(packed_bots, file)
        file.close()
        send_message('To load this snapshot later, type \"!load @' + nickname + ' ' + filename + '\".', this_message)
        send_message('Snapshot summary:\n' + '\n'.join(bot_names), this_message)
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Created snapshot and sent to \"' + sender + '\".')
        return filepath
    except:
        send_message('Failed to create snapshot.')
        return None

def load_snapshot(filename, this_message=None, sender='(system)'):
    send_message('Loading bots from snapshot: ' + filename, this_message)
    try:
        filepath = os.path.join(snapshot_dir, filename)
        if ('\\' in filename) or ('/' in filename) or (not filename.lower().endswith('.json')) or (os.path.dirname(os.path.realpath(filepath)).lower() != snapshot_dir.lower()) or not (os.path.isfile(filepath)):
            if snapshot_filepath != None:
                send_message('The specified snapshot could not be found. Restoring snapshot created just now...', this_message)
                filepath = snapshot_filepath
            else:
                send_message('The specified snapshot could not be found.', this_message)
                return
        file = open(filepath, 'r')
        packed_bots = json.load(file)
        file.close()
        for packed_bot in packed_bots:
            bot = bot_thread(packed_bot['nickname'][:36], bot_data_parser(packed_bot['data']), packed_bot['room'], packed_bot['creator'])
            bots.append(bot)
            try:
                bot.paused = packed_bot['paused']
            except KeyError:
                pass
            try:
                bot.pause_text = packed_bot['pauseText']
            except KeyError:
                pass
            bot.start()
        send_message('Successfully loaded snapshot.', this_message)
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Loaded snapshot at \"' + filename + '\" from \"' + sender + '\".')
    except:
        send_message('Failed to load snapshot.', this_message)
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Failed to load snapshot at \"' + filename + '\" from \"' + sender + '\".')

def killall_and_load_snapshot(filename, this_message=None, sender='(system)'):
    global bots
    send_message('A snapshot will be created so that the current state can be restored if necessary.', this_message)
    snapshot_filepath = create_snapshot(this_message, sender)
    send_message('Killing all bots...', this_message)
    while len(bots) > 0:
        bots.pop().kill()
    load_snapshot(filename, this_message, sender)

##def get_available_snapshots(nearest_to=None):
##    if nearest_to == None:
##        nearest_to = datetime.datetime.now()
##    available_snapshots = []
##    for snapshot in os.listdir(snapshot_dir):
##        if snapshot_matching_regex.match(snapshot):
##            available_snapshots.append(snapshot)
##    return available_snapshots

send_nick()
send_message('/me Hello, world!')
uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Connected!')
uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Attempting to load most recent snapshot...')
latest_snapshot_filename = None
latest_snapshot = None
snapshot_matching_regex = re.compile('^(\\d+)-(\\d+)-(\\d+)_(\\d\\d)(\\d\\d)(\\d\\d)(?:_(\\d+))?\.json$', re.IGNORECASE)
for snapshot in os.listdir(snapshot_dir):
    m = snapshot_matching_regex.match(snapshot)
    if m:
        g = tuple(map(int, m.groups('0')))
        if latest_snapshot == None:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
        if g[2] > latest_snapshot[2]:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
        if g[2] < latest_snapshot[2]:
            continue
        if g[0] > latest_snapshot[0]:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
        if g[0] < latest_snapshot[0]:
            continue
        if g[1] > latest_snapshot[1]:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
        if g[1] < latest_snapshot[1]:
            continue
        if g[3] > latest_snapshot[3]:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
        if g[3] < latest_snapshot[3]:
            continue
        if g[4] > latest_snapshot[4]:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
        if g[4] < latest_snapshot[4]:
            continue
        if g[5] > latest_snapshot[5]:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
        if g[5] < latest_snapshot[5]:
            continue
        if g[6] > latest_snapshot[6]:
            latest_snapshot = g
            latest_snapshot_filename = snapshot
            continue
if latest_snapshot == None:
    send_message('Found no snapshots to restore.')
else:
    load_snapshot(latest_snapshot_filename)

while True:
    try:
        data = ws.recv()
    except WebSocketConnectionClosedException:
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Disconnected. Attempting to reconnect...')
        ws = create_connection(web_socket_url)
        send_nick()
        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Reconnected!')
        data = ws.recv()
    data = json.loads(data)
    if data['type'] == 'ping-event':
        send_ping()
    if data['type'] == 'nick-reply':
        agent_id = data['data']['id']
    if data['type'] == 'send-event':
        content = data['data']['content']
        parent = data['data']['parent']
        this_message = data['data']['id']
        sender = data['data']['sender']['name']
        sender_agent_id = data['data']['sender']['id']
        send_time = data['data']['time']

        if len(content) > 0 and content[0] == '!':
            if content[1:].lower() == 'ping':
                send_message('Pong!', this_message)
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Ponged to a ping from \"' + sender + '\".')
            elif (len(content) == 7 + len(nickname) or (len(content) >= 7 + len(nickname) and content[7+len(nickname)] == ' ')) and content[1:7+len(nickname)].lower() == ('list @' + nickname).lower():
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                new_bots = []
                bot_names = []
                for bot in bots:
                    if not bot.finished:
                        new_bots.append(bot)
                        if not bot.paused:
                            if bot.room_name != room_name:
                                bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ')')
                            else:
                                bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\")')
                        else:
                            if bot.room_name != room_name:
                                bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ') (paused)')
                            else:
                                bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (paused)')
                bots = new_bots
                if len(bot_names) == 0:
                    send_message('No bots created with @' + nickname + ' are running.', this_message)
                else:
                    send_message('Currently running bots created with @' + nickname + ':\n' + '\n'.join(bot_names), this_message)
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Listed bots by request from \"' + sender + '\".')
            elif (len(content) == 7 + len(nickname) or (len(content) >= 7 + len(nickname) and content[7+len(nickname)] == ' ')) and content[1:7+len(nickname)].lower() == ('help @' + nickname).lower():
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                send_message(help_text, this_message)
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Sent help text to \"' + sender + '\".')
            elif (len(content) == 10 + len(nickname) or (len(content) >= 10 + len(nickname) and content[10+len(nickname)] == ' ')) and content[1:10+len(nickname)].lower() == ('killall @' + nickname).lower():
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                send_message('Killing all bots...', this_message)
                while len(bots) > 0:
                    bots.pop().announce_and_kill(this_message)
                uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Killed all bots by request from \"' + sender + '\".')
            elif len(content) > 13 and content[1:12].lower() == 'createbot @':
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                parse_tree = content.split(' ', 2)
                if len(parse_tree) < 3:
                    continue
                bot_nickname = parse_tree[1][1:][:36]
                try:
                    bot_data = bot_data_parser(parse_tree[2])
                    bot = bot_thread(bot_nickname, bot_data, room_name, sender)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + '.', this_message)
                    uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Created @' + bot_nickname + ' by request from \"' + sender + '\".')
                except:
                    send_message('Failed to create @' + bot_nickname + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]), this_message)
            elif len(content) > 13 and content[1:12].lower() == 'createbot &':
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                parse_tree = content.split(' ', 3)
                if len(parse_tree) < 4:
                    continue
                if len(parse_tree[2]) < 2 or parse_tree[2][0] != '@':
                    continue
                bot_nickname = parse_tree[2][1:][:36]
                try:
                    bot_data = bot_data_parser(parse_tree[3])
                    bot = bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), sender)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                    uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Created @' + bot_nickname + ' by request from \"' + sender + '\" in &' + parse_tree[1][1:].lower() + '.')
                except:
                    send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]), this_message)
            elif len(content) > 17 and content[1:16].lower() == 'createtestbot @':
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                send_message('Note: The !createtestbot command has been deprecated. Use !createbot instead.', this_message)
                parse_tree = content.split(' ', 2)
                if len(parse_tree) < 3:
                    continue
                bot_nickname = parse_tree[1][1:][:36]
                try:
                    bot_data = bot_data_parser(parse_tree[2])
                    bot = bot_thread(bot_nickname, bot_data, room_name, sender)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + '.', this_message)
                    uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Created @' + bot_nickname + ' by request from \"' + sender + '\".')
                except:
                    send_message('Failed to create @' + bot_nickname + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]), this_message)
            elif len(content) > 17 and content[1:16].lower() == 'createtestbot &':
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                send_message('Note: The !createtestbot command has been deprecated. Use !createbot instead.', this_message)
                parse_tree = content.split(' ', 3)
                if len(parse_tree) < 4:
                    continue
                if len(parse_tree[2]) < 2 or parse_tree[2][0] != '@':
                    continue
                bot_nickname = parse_tree[2][1:][:36]
                try:
                    bot_data = bot_data_parser(parse_tree[3])
                    bot = bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), sender)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                    uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Created @' + bot_nickname + ' by request from \"' + sender + '\" in &' + parse_tree[1][1:].lower() + '.')
                except:
                    send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]), this_message)
            elif len(content) > 11 and content[1:10].lower() == 'sendbot &':
                desired_bots = []
                parse_tree = content.split(' ', 4)
                if len(parse_tree) < 3:
                    continue
                if len(parse_tree[2]) < 2 or parse_tree[2][0] != '@':
                    continue
                bot_nickname = parse_tree[2][1:][:36]
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                    if bot_nickname.lower() == bot.nickname.lower():
                        desired_bots.append(bot)
                if dont_respond:
                    continue
                if len(desired_bots) == 0:
                    send_message('No bot named @' + bot_nickname + ' was found.', this_message)
                elif len(desired_bots) == 1:
                    try:
                        bot_data = bot_data_parser(desired_bots[0].data.parse_string)
                        bot = bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), desired_bots[0].creator)
                        bots.append(bot)
                        bot.start()
                        send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                        uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Copied @' + bot_nickname + ' by request from \"' + sender + '\" to &' + parse_tree[1][1:].lower() + '.')
                    except:
                        send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                        send_message('Error details:\n' + str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]), this_message)
                else:
                    try:
                        desired_bots = [desired_bots[int(parse_tree[3]) - 1]]
                        try:
                            bot_data = bot_data_parser(desired_bots[0].data.parse_string)
                            bot = bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), desired_bots[0].creator)
                            bots.append(bot)
                            bot.start()
                            send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                            uniprint('[' + datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '] Copied @' + bot_nickname + ' by request from \"' + sender + '\" to &' + parse_tree[1][1:].lower() + '.')
                        except:
                            send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                            send_message('Error details:\n' + str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]), this_message)
                    except:
                        bot_names = []
                        for bot in desired_bots:
                            if not bot.paused:
                                if bot.room_name != room_name:
                                    bot_names.append(str(len(bot_names) + 1) + ': @' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ')')
                                else:
                                    bot_names.append(str(len(bot_names) + 1) + ': @' + bot.nickname + ' (created by \"' + bot.creator + '\")')
                            else:
                                if bot.room_name != room_name:
                                    bot_names.append(str(len(bot_names) + 1) + ': @' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ') (paused)')
                                else:
                                    bot_names.append(str(len(bot_names) + 1) + ': @' + bot.nickname + ' (created by \"' + bot.creator + '\") (paused)')
                        send_message('More than one bot named @' + bot_nickname + ' was found. Please select the correct bot by using the command \"!sendbot ' + parse_tree[1].lower() + ' @' + bot_nickname + ' (number of desired bot)\".\n' + '\n'.join(bot_names), this_message)
            elif (len(content) == 7 + len(nickname) or (len(content) >= 7 + len(nickname) and content[7+len(nickname)] == ' ')) and content[1:7+len(nickname)].lower() == ('save @' + nickname).lower():
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                create_snapshot(this_message, sender)
##            elif len(content) == 7 + len(nickname) and content[1:7+len(nickname)].lower() == ('load @' + nickname).lower():
##                available_snapshots = get_available_snapshots()
##                if len(available_snapshots) == 0:
##                    send_message('There are no available snapshots.', this_message)
            elif len(content) > 7 + len(nickname) and content[1:8+len(nickname)].lower() == ('load @' + nickname + ' ').lower():
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                filename = content.split(' ', 2)[2]
                if filename.lower() == 'latest':
                    latest_snapshot_filename = None
                    latest_snapshot = None
                    for snapshot in os.listdir(snapshot_dir):
                        m = snapshot_matching_regex.match(snapshot)
                        if m:
                            g = tuple(map(int, m.groups('0')))
                            if latest_snapshot == None:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                            if g[2] > latest_snapshot[2]:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                            if g[2] < latest_snapshot[2]:
                                continue
                            if g[0] > latest_snapshot[0]:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                            if g[0] < latest_snapshot[0]:
                                continue
                            if g[1] > latest_snapshot[1]:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                            if g[1] < latest_snapshot[1]:
                                continue
                            if g[3] > latest_snapshot[3]:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                            if g[3] < latest_snapshot[3]:
                                continue
                            if g[4] > latest_snapshot[4]:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                            if g[4] < latest_snapshot[4]:
                                continue
                            if g[5] > latest_snapshot[5]:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                            if g[5] < latest_snapshot[5]:
                                continue
                            if g[6] > latest_snapshot[6]:
                                latest_snapshot = g
                                latest_snapshot_filename = snapshot
                                continue
                    if latest_snapshot == None:
                        send_message('Found no snapshots to load.', this_message)
                        continue
                    else:
                        filename = latest_snapshot_filename
                killall_and_load_snapshot(filename, this_message, sender)
            elif (len(content) == 10 + len(nickname) or (len(content) >= 10 + len(nickname) and content[10+len(nickname)] == ' ')) and content[1:10+len(nickname)].lower() == ('restart @' + nickname).lower():
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                send_message('Creating snapshot...', this_message)
                create_snapshot(this_message, sender)
                send_message('Killing all bots...', this_message)
                while len(bots) > 0:
                    bots.pop().kill()
                send_message('/me is restarting...', this_message)
                sys.exit(0)
