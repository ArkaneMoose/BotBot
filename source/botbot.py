#Standard library modules
import json
import time
import sys
import os
import random
import threading

import re
import traceback

#Additional modules
from websocket import create_connection, WebSocketConnectionClosedException

#Project modules
import logger
import bot_parser
import bot_thread as bt

log = logger.Logger()

help_text = ""
with open("data/help.txt") as f:
    help_text = f.read()

room_name = 'testing'
nickname = 'BotBot'
snapshot_dir = None

bots = bt.bots

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            if len(sys.argv) > 3:
                print('Usage: python3 ' + sys.argv[0] + ' <room name> (default room: ' + room_name + ') <nickname> (default nickname: ' + nickname + ')')
                sys.exit(1)
            nickname = sys.argv[2]
        room_name = sys.argv[1]

web_socket_url = 'wss://euphoria.io/room/{}/ws'.format(room_name)
log.write('Connecting to ' + web_socket_url + ' as ' + nickname + '...')
ws = create_connection(web_socket_url)
mid = 0
agent_id = None

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

def send_get_message(id):
    global mid
    global ws
    message = {'type':'get-message','data':{'id':id},'id':str(mid)}
    message = json.dumps(message)
    send(message)
    mid += 1

def create_snapshot(this_message=None, sender='(System)'):
    if not snapshot_dir:
        send_message('Snapshots are not enabled for this instance of @' + nickname + '.', this_message)
        return
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
        log.write('Created snapshot and sent to \"' + sender + '\".')
        return filepath
    except:
        send_message('Failed to create snapshot.')
        return None

def load_snapshot(filename, this_message=None, sender='(system)'):
    if not snapshot_dir:
        send_message('Snapshots are not enabled for this instance of @' + nickname + '.', this_message)
        return
    if filename.lower() == 'latest':
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
        return
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
            bot = bt.bot_thread(packed_bot['nickname'][:36], bot_parser.Parser(packed_bot['data']), packed_bot['room'], agent_id, packed_bot['creator'])
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
        log.write('Loaded snapshot at \"' + filename + '\" from \"' + sender + '\".')
    except:
        send_message('Failed to load snapshot.', this_message)
        log.write('Failed to load snapshot at \"' + filename + '\" from \"' + sender + '\".')

def killall_and_load_snapshot(filename, this_message=None, sender='(system)'):
    if not snapshot_dir:
        send_message('Snapshots are not enabled for this instance of @' + nickname + '.', this_message)
        return
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
log.write('Connected!')
log.write('Attempting to load most recent snapshot...')
load_snapshot('latest')

while True:
    try:
        data = ws.recv()
    except WebSocketConnectionClosedException:
        log.write('Disconnected. Attempting to reconnect...')
        ws = create_connection(web_socket_url)
        send_nick()
        log.write(' Reconnected!')
        data = ws.recv()
    data = json.loads(data)
    if data['type'] == 'ping-event':
        send_ping()
    if data['type'] == 'nick-reply':
        agent_id = data['data']['id']
        for bot in bots:
            bot.botbot_agent_id = agent_id
    if data['type'] in ('send-event', 'get-message-reply'):
        content = data['data']['content']
        parent = data['data'].get('parent')
        this_message = data['data']['id']
        sender = data['data']['sender']['name']
        sender_agent_id = data['data']['sender']['id']
        send_time = data['data']['time']

        if data['data'].get('truncated'):
            send_get_message(data['data']['id'])
        elif len(content) > 0 and content[0] == '!':
            if content[1:].lower() == 'ping':
                send_message('Pong!', this_message)
                log.write('Ponged to a ping from \"' + sender + '\".')
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
                log.write('Listed bots by request from \"' + sender + '\".')
            elif (len(content) == 7 + len(nickname) or (len(content) >= 7 + len(nickname) and content[7+len(nickname)] == ' ')) and content[1:7+len(nickname)].lower() == ('help @' + nickname).lower():
                dont_respond = False
                for bot in bots:
                    if sender_agent_id == bot.agent_id:
                        dont_respond = True
                        break
                if dont_respond:
                    continue
                send_message(help_text, this_message)
                log.write('Sent help text to \"' + sender + '\".')
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
                log.write('Killed all bots by request from \"' + sender + '\".')
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
                    bot_data = bot_parser.Parser(parse_tree[2])
                    bot = bt.bot_thread(bot_nickname, bot_data, room_name, sender, agent_id, log)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + '.', this_message)
                    log.write('Created @' + bot_nickname + ' by request from \"' + sender + '\".')
                except:
                    send_message('Failed to create @' + bot_nickname + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), this_message)
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
                    bot_data = bot_parser.Parser(parse_tree[3])
                    bot = bt.bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), agent_id, sender)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                    log.write('Created @' + bot_nickname + ' by request from \"' + sender + '\" in &' + parse_tree[1][1:].lower() + '.')
                except:
                    send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), this_message)
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
                    bot_data = bot_parser.Parser(parse_tree[2])
                    bot = bt.bot_thread(bot_nickname, bot_data, room_name, sender, agent_id, log)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + '.', this_message)
                    log.write('Created @' + bot_nickname + ' by request from \"' + sender + '\".')
                except:
                    send_message('Failed to create @' + bot_nickname + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), this_message)
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
                    bot_data = bot_parser.Parser(parse_tree[3])
                    bot = bt.bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), sender, agent_id, log)
                    bots.append(bot)
                    bot.start()
                    send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                    log.write('Created @' + bot_nickname + ' by request from \"' + sender + '\" in &' + parse_tree[1][1:].lower() + '.')
                except:
                    send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                    send_message('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), this_message)
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
                        bot_data = bot_parser.Parser(desired_bots[0].data.parse_string)
                        bot = bt.bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), desired_bots[0].creator, agent_id, log)
                        bots.append(bot)
                        bot.start()
                        send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                        log.write('Copied @' + bot_nickname + ' by request from \"' + sender + '\" to &' + parse_tree[1][1:].lower() + '.')
                    except:
                        send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                        send_message('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), this_message)
                else:
                    try:
                        desired_bots = [desired_bots[int(parse_tree[3]) - 1]]
                        try:
                            bot_data = bot_parser.Parser(desired_bots[0].data.parse_string)
                            bot = bt.bot_thread(bot_nickname, bot_data, parse_tree[1][1:].lower(), desired_bots[0].creator, agent_id, log)
                            bots.append(bot)
                            bot.start()
                            send_message('Created @' + bot_nickname + ' in ' + parse_tree[1].lower() + '.', this_message)
                            log.write('Copied @' + bot_nickname + ' by request from \"' + sender + '\" to &' + parse_tree[1][1:].lower() + '.')
                        except:
                            send_message('Failed to create @' + bot_nickname + ' in ' + parse_tree[1].lower() + '. Is your code valid?', this_message)
                            send_message('Error details:\n' + ''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])), this_message)
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
