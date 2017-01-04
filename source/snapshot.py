import os
import traceback
import errno
import datetime
import json
import shutil
import time

import botbot.logger as logger

log = logger.Logger()

class Snapshot:
    snapshot_dir = ""

    @classmethod
    def is_enabled(cls):
        return bool(cls.snapshot_dir)

    @classmethod
    def pack_bot(cls, bot):
        variables = dict(bot.variables)
        if 'variables' in variables:
            del variables['variables']
        return json.dumps({
            'nickname': bot.nickname,
            'code': bot.code_struct.parse_string,
            'room': bot.room_name,
            'password': bot.password,
            'creator': bot.creator,
            'paused': bot.paused,
            'pauseText': bot.pause_text,
            'uuid': bot.uuid,
            'variables': variables
        })

    @classmethod
    def create(cls, bots):
        if not cls.is_enabled():
            return ['Snapshots are not enabled.']

        try:
            bot_count = len(os.listdir(os.path.join(cls.snapshot_dir, 'current')))
            if bot_count == 0:
                return ['There are no running bots. A snapshot will not be created.']
        except OSError as err:
            if err.errno == errno.ENOENT:
                return ['There are no running bots. A snapshot will not be created.']

        # Create snapshot directory if it does not exist
        try:
            os.makedirs(cls.snapshot_dir)
        except OSError as err:
            if err.errno != errno.EEXIST or not os.path.isdir(cls.snapshot_dir):
                traceback.print_exc()
                return ["Snapshot directory could not be created."]

        basename = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filepath_from_basename = os.path.join(cls.snapshot_dir, basename)

        #Dump the bots to the file
        try:
            filepath = shutil.make_archive(filepath_from_basename, 'gztar', os.path.join(cls.snapshot_dir, 'current'))
        except OSError:
            return ["Snapshot file could not be written."]
        filename = os.path.relpath(filepath, cls.snapshot_dir)

        msg_to_load_later = ('To load this snapshot later, type \"!load @BotBot ' +
            filename + '\".\n' + str(bot_count) + ' bot' +
            ('s' if bot_count != 1 else '') + ' saved.')
        msg_latest_symlink_fail = ('Note: \"latest\" file could not be written. '
            '\"!load @BotBot latest\" will not work as expected.')

        try:
            os.unlink(os.path.join(cls.snapshot_dir, "latest"))
        except OSError as err:
            if err.errno != errno.ENOENT:
                traceback.print_exc()
                return [msg_to_load_later, msg_latest_symlink_fail]
        except FileNotFoundError:
            pass
        except:
            traceback.print_exc()
            return [msg_to_load_later, msg_latest_symlink_fail]

        try:
            os.symlink(filename, os.path.join(cls.snapshot_dir, "latest"))
        except:
            traceback.print_exc()
            return [msg_to_load_later, msg_latest_symlink_fail]

        return [msg_to_load_later]

    @classmethod
    def get_filepath(cls, filename):
        if not cls.is_enabled():
            return None
        filepath = os.path.join(cls.snapshot_dir, filename)
        if not os.path.isfile(filepath): return None
        filepath = os.path.realpath(filepath)
        if os.path.dirname(filepath) != os.path.realpath(cls.snapshot_dir): return None
        return filepath

    @classmethod
    def load(cls, filepath, bots):
        if not cls.is_enabled():
            return ['Snapshots are not enabled.']

        rm_errors = False
        try:
            shutil.rmtree(os.path.join(cls.snapshot_dir, 'current'))
        except:
            if os.path.isdir(os.path.join(cls.snapshot_dir, 'current')):
                traceback.print_exc()
                rm_errors = True

        try:
            shutil.unpack_archive(filepath, os.path.join(cls.snapshot_dir, 'current'), 'gztar')
        except:
            return ['Could not unpack snapshot. Please verify that it exists.']

        messages = cls.load_current(bots)
        if rm_errors:
            messages.append(('Note: There were errors removing some files. '
                'Unexpected behavior may occur in the next snapshot.'))
        return messages

    @classmethod
    def load_current(cls, bots):
        if not cls.is_enabled():
            return ['Snapshots are not enabled.']

        current_dir = os.path.join(cls.snapshot_dir, 'current')

        try:
            os.makedirs(current_dir)
        except OSError as err:
            if err.errno != errno.EEXIST or not os.path.isdir(current_dir):
                traceback.print_exc()
                return ["Snapshot directory could not be created."]

        packed_bots_list = os.listdir(current_dir)
        failed_bots = 0

        try:
            for packed_bot_filename in packed_bots_list:
                if not packed_bot_filename.endswith('.json'):
                    continue
                try:
                    with open(os.path.join(current_dir, packed_bot_filename)) as f:
                        packed_bot = json.load(f)
                    bots.create(packed_bot['nickname'][:36],
                        packed_bot['room'],
                        packed_bot.get('password', None),
                        packed_bot['creator'],
                        packed_bot['code'],
                        paused=packed_bot.get('paused', False),
                        pause_text=packed_bot.get('pauseText', ''),
                        uuid=packed_bot.get('uuid', None),
                        variables=packed_bot.get('variables', None)
                    )
                except:
                    log.write('Failed to load ' + packed_bot_filename + ' from snapshot.')
                    traceback.print_exc()
                    failed_bots += 1
                #sleep for 1 second to stagger bot loads
                #this should alleviate some server burden
                time.sleep(1)
        except OSError:
            return ['Could not read bots from unpacked snapshot.']

        return ['Successfully loaded ' + str(len(packed_bots_list) - failed_bots) +
            ' of ' + str(len(packed_bots_list)) + ' bot' +
            ('s' if len(packed_bots_list) != 1 else '') +
            ' from snapshot.']
