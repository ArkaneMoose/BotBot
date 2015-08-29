import os
import errno
import datetime
import json

from botbotbot import BotBotBot

snapshot_dir = "snapshots"

# This class does not work.
# It needs to be updated to work with the new BotBot architecture.
# It currently serves as a placeholder so that other code works.

class Snapshot:
    def is_enabled():
        return bool(snapshot_dir)

    def create(bots):
        if not Snapshot.is_enabled():
            return ['Snapshots are not enabled.']

        #Pack all the bots together
        packed_bots = []
        bot_names = []
        for bot in bots.execs:
            packed_bots.append({'nickname': bot.nickname, 'code': bot.code_struct.parse_string, 'room': bot.room_name, 'creator': bot.creator, 'paused': bot.paused, 'pauseText': bot.pause_text})
            if not bot.paused:
                if bot.room_name != bots.botbot.room_name:
                    bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ')')
                else:
                    bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\")')
            else:
                if bot.room_name != room_name:
                    bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (in &' + bot.room_name + ') (paused)')
                else:
                    bot_names.append('@' + bot.nickname + ' (created by \"' + bot.creator + '\") (paused)')

        if len(packed_bots) == 0:
            return ['There are no running bots. A snapshot will not be created.']

        formatted_datetime = datetime.datetime.now().strftime('%m-%d-%Y_%H%M%S')
        filename = formatted_datetime + '.json'
        filepath = os.path.join(snapshot_dir, filename)

        #Dump the bots to the file
        try:
            with open(filepath, 'w') as dumpfile:
                dumpfile.write(json.dumps(packed_bots))
        except FileNotFoundError:
            return ["Snapshot file could not be opened."]

        try:
            os.unlink(os.path.join(snapshot_dir, "latest"))
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
        os.symlink(filename, os.path.join(snapshot_dir, "latest"))

        return ['To load this snapshot later, type \"!load @BotBot ' + filename + '\".', 'Snapshot summary:\n' + '\n'.join(bot_names)]

    def get_filepath(filename):
        filepath = os.path.join(snapshot_dir, filename)
        if not os.path.isfile(filepath): return None
        filepath = os.path.realpath(filepath)
        if os.path.dirname(filepath) != os.path.realpath(snapshot_dir): return None
        return filepath

    def load(filepath, bots):
        if not snapshot_dir:
            return ['Snapshots are not enabled.']

        try:
            with open(filepath, 'r') as f:
                packed_bots = json.loads(f.read())
        except FileNotFoundError:
            return ['Could not find snapshot.']

        for packed_bot in packed_bots:
            bot = bots.create(packed_bot['nickname'][:36], packed_bot['room'], None, packed_bot['creator'], packed_bot['code'])
            if "paused" in packed_bot:
                bot.paused = packed_bot['paused']
            if "pauseText" in packed_bot:
                bot.pause_text = packed_bot['pauseText']

        return ['Successfully loaded snapshot.']
