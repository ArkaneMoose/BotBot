import os

snapshot_dir = None

# This class does not work.
# It needs to be updated to work with the new BotBot architecture.
# It currently serves as a placeholder so that other code works.

class Snapshot:
    def is_enabled():
        return bool(snapshot_dir)
    
    def create(this_message=None, sender='(system)'):
        if not snapshot_dir:
            return (None, ['Snapshots are not enabled.'])
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

    def load(filename, this_message=None, sender='(system)'):
        if not snapshot_dir:
            return (False, ['Snapshots are not enabled.'])
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

##def killall_and_load_snapshot(filename, this_message=None, sender='(system)'):
##    if not snapshot_dir:
##        send_message('Snapshots are not enabled for this instance of @' + nickname + '.', this_message)
##        return
##    global bots
##    send_message('A snapshot will be created so that the current state can be restored if necessary.', this_message)
##    snapshot_filepath = create_snapshot(this_message, sender)
##    send_message('Killing all bots...', this_message)
##    while len(bots) > 0:
##        bots.pop().kill()
##    load_snapshot(filename, this_message, sender)
