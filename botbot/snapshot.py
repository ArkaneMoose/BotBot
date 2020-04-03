import os
import traceback
import errno
import datetime
import json
import shutil
import time

from . import logger

log = logger.Logger()
snapshot_dir = ""

def is_enabled():
    return bool(snapshot_dir)

def pack_bot(bot):
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
        'initialized': bot.initialized,
        'variables': variables
    })

def create(bots):
    if not is_enabled():
        return ['Snapshots are not enabled.']

    try:
        bot_count = sum(filepath.endswith('.json') for filepath
            in os.listdir(os.path.join(snapshot_dir, 'current')))
        if bot_count == 0:
            return ['There are no running bots. A snapshot will not be created.']
    except OSError as err:
        if err.errno == errno.ENOENT:
            return ['There are no running bots. A snapshot will not be created.']

    # Create snapshot directory if it does not exist
    try:
        os.makedirs(snapshot_dir)
    except OSError as err:
        if err.errno != errno.EEXIST or not os.path.isdir(snapshot_dir):
            traceback.print_exc()
            return ["Snapshot directory could not be created."]

    basename = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filepath_from_basename = os.path.join(snapshot_dir, basename)

    #Dump the bots to the file
    try:
        filepath = shutil.make_archive(filepath_from_basename, 'gztar', os.path.join(snapshot_dir, 'current'))
    except OSError:
        return ["Snapshot file could not be written."]
    filename = os.path.relpath(filepath, snapshot_dir)

    msg_to_load_later = ('To load this snapshot later, type \"!load @BotBot ' +
        filename + '\".\n' + str(bot_count) + ' bot' +
        ('s' if bot_count != 1 else '') + ' saved.')
    msg_latest_symlink_fail = ('Note: \"latest\" file could not be written. '
        '\"!load @BotBot latest\" will not work as expected.')

    try:
        os.unlink(os.path.join(snapshot_dir, "latest"))
    except OSError as err:
        if err.errno != errno.ENOENT:
            traceback.print_exc()
            return [msg_to_load_later, msg_latest_symlink_fail]
    except FileNotFoundError:
        pass
    except Exception:
        traceback.print_exc()
        return [msg_to_load_later, msg_latest_symlink_fail]

    try:
        os.symlink(filename, os.path.join(snapshot_dir, "latest"))
    except Exception:
        traceback.print_exc()
        return [msg_to_load_later, msg_latest_symlink_fail]

    return [msg_to_load_later]

def get_filepath(filename):
    if not is_enabled():
        return None
    filepath = os.path.join(snapshot_dir, filename)
    if not os.path.isfile(filepath): return None
    filepath = os.path.realpath(filepath)
    if os.path.dirname(filepath) != os.path.realpath(snapshot_dir): return None
    return filepath

def load(filepath, bots):
    if not is_enabled():
        return ['Snapshots are not enabled.']

    rm_errors = False
    try:
        shutil.rmtree(os.path.join(snapshot_dir, 'current'))
    except Exception:
        if os.path.isdir(os.path.join(snapshot_dir, 'current')):
            traceback.print_exc()
            rm_errors = True

    try:
        shutil.unpack_archive(filepath, os.path.join(snapshot_dir, 'current'), 'gztar')
    except Exception:
        return ['Could not unpack snapshot. Please verify that it exists.']

    messages = load_current(bots)
    if rm_errors:
        messages.append(('Note: There were errors removing some files. '
            'Unexpected behavior may occur in the next snapshot.'))
    return messages

def load_current(bots):
    if not is_enabled():
        return ['Snapshots are not enabled.']

    current_dir = os.path.join(snapshot_dir, 'current')

    try:
        os.makedirs(current_dir)
    except OSError as err:
        if err.errno != errno.EEXIST or not os.path.isdir(current_dir):
            traceback.print_exc()
            return ["Snapshot directory could not be created."]

    packed_bots_list = os.listdir(current_dir)
    loaded_bots = 0
    total_bots = 0

    try:
        for packed_bot_filename in packed_bots_list:
            if not packed_bot_filename.endswith('.json'):
                continue

            total_bots += 1
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
                    variables=packed_bot.get('variables', None),
                    initialized=packed_bot.get('initialized', False)
                )
            except Exception:
                log.write('Failed to load ' + packed_bot_filename + ' from snapshot.')
                traceback.print_exc()
            else:
                loaded_bots += 1

            # sleep for 1 second to stagger bot loads
            # this should alleviate some server burden
            time.sleep(1)
    except OSError:
        return ['Could not read bots from unpacked snapshot.']

    return ['Successfully loaded ' + str(loaded_bots) + ' of ' +
        str(total_bots) + ' bot' + ('s' if total_bots != 1 else '') +
        ' from snapshot.']
