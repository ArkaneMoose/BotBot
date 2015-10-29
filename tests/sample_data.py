import random
import string
import builtins

# This module provides random sample data for any given type according to the
# Heim specifications detailed at
# https://github.com/euphoria-io/heim/blob/master/doc/api.md

def bool(**kwargs):
    """Random boolean (True or False)."""
    if 'value' not in kwargs:
        value = random.random() < 0.5
    else:
        value = builtins.bool(value)
    return value

class int(builtins.int):
    """Random 64-bit signed integer."""
    def __new__(cls, **kwargs):
        if 'value' not in kwargs:
            unsigned = random.getrandbits(64)
            value = (unsigned >> 1) if unsigned >= 2 ** 63 else ~(unsigned >> 1)
        else:
            value = kwargs['value']
        return super().__new__(cls, value)

class string(str):
    """Random string of printable characters unless specified of a random length
    between 0 and 255 characters unless specified."""
    def __new__(cls, alphabet=string.printable, **kwargs):
        if 'value' not in kwargs:
            if 'length' not in kwargs:
                length = random.randrange(256)
            else:
                length = builtins.int(kwargs['length'])
            value = ''.join(random.choice(alphabet) for _ in range(length))
        else:
            value = kwargs['value']
        return super().__new__(cls, value)

class object(dict):
    """Random JSON object, which is implemented as a dict with a random number
    from 0 to 31 unless specified of random keys with random values."""
    def __init__(self, **kwargs):
        super().__init__()
        if 'value' not in kwargs:
            if 'keys' not in kwargs:
                keys = random.randrange(32)
            else:
                keys = builtins.int(kwargs['keys'])
            while len(self.keys()) < keys:
                self[string(length=random.randrange(32))] = random.choice((lambda: bool(), lambda: int(), lambda: string()))()
        else:
            value = dict(kwargs['value'])
            for key in value:
                self[key] = value

class AccountView(dict):
    """Randomly generated AccountView, unless parameters are specified."""
    def __init__(self, **kwargs):
        super().__init__()
        if 'id' not in kwargs:
            self['id'] = Snowflake()
        else:
            self['id'] = Snowflake(value=kwargs['id'])
        if 'name' not in kwargs:
            self['name'] = string(length=random.randint(1, 31))
        else:
            self['name'] = string(value=kwargs['name'])

class AuthOption(str):
    """Random AuthOption, unless specified."""
    def __new__(cls, **kwargs):
        possible_values = ('passcode')
        if 'value' not in kwargs:
            value = random.choice(possible_values)
        else:
            value = kwargs['value']
            if value not in possible_values:
                raise SyntaxError('invalid AuthOption')
        return super().__new__(cls, value)

class Message(dict):
    """Random Message. Each optional field has a 50%\ chance of being present
    unless specified."""
    def __init__(self, **kwargs):
        super().__init__()
        required_attrs = (('id', Snowflake), ('time', Time), ('sender', SessionView), ('content', string))
        optional_attrs = (('parent', Snowflake), ('previous_edit_id', Snowflake), ('encryption_key_id', string), ('edited', Time), ('deleted', Time), ('truncated', lambda **x: True))
        for attr in required_attrs:
            if attr[0] not in kwargs:
                self[attr[0]] = attr[1]()
            else:
                self[attr[0]] = attr[1](value=kwargs[attr[0]])
        for attr in optional_attrs:
            if attr[0] not in kwargs:
                if bool():
                    self[attr[0]] = attr[1]()
            else:
                if kwargs[attr[0]] != None:
                    self[attr[0]] = attr[1](value=kwargs[attr[0]])

class PacketType(str):
    """Random PacketType, unless specified."""
    def __new__(cls, type='all', **kwargs):
        possible_values = {'session-management-command': ('auth', 'ping'),
        'chat-room-command': ('get-message', 'log', 'nick', 'send', 'who'),
        'account-management-command': ('change-name', 'change-password',
        'login', 'logout', 'register-account', 'reset-password'),
        'room-manager-command': ('ban', 'edit-message', 'grant-access',
        'grant-manager', 'revoke-access', 'revoke-manager', 'unban'),
        'staff-command': ('staff-create-room', 'staff-grant-manager',
        'staff-lock-room', 'staff-revoke-access', 'staff-revoke-manager',
        'unlock-staff-capability'),
        'event': ('bounce-event', 'disconnect-event', 'edit-message-event',
        'hello-event', 'join-event', 'network-event', 'nick-event',
        'part-event', 'ping-event', 'send-event', 'snapshot-event')}
        possible_values_keys = tuple(possible_values.keys())
        for possible_packet_type in possible_values_keys:
            if possible_packet_type.endswith('-command'):
                possible_values[possible_packet_type[:-len('-command')] + '-reply'] = tuple(map(lambda x: x + '-reply', possible_values[possible_packet_type]))
                possible_values['command'] = possible_values.get('command', ()) + possible_values[possible_packet_type]
                possible_values['reply'] = possible_values.get('reply', ()) + possible_values[possible_packet_type[:-len('-command')] + '-reply']
        possible_values['all'] = possible_values['command'] + possible_values['reply'] + possible_values['event']
        if 'value' not in kwargs:
            value = random.choice(possible_values[type])
        else:
            value = kwargs['value']
            if value not in possible_values['all']:
                raise SyntaxError('invalid PacketType')
        return super().__new__(cls, value)

class SessionView(dict):
    """Random SessionView. Each optional field has a 50%\ chance of being
    present unless specified."""
    def __init__(self, **kwargs):
        super().__init__()
        required_attrs = (('id', UserID), ('name', lambda **x: string(length=random.randint(1, 36), **x)), ('server_id', string), ('server_era', string), ('session_id', string))
        optional_attrs = (('is_staff', lambda **x: True), ('is_manager', lambda **x: True))
        for attr in required_attrs:
            if attr[0] not in kwargs:
                self[attr[0]] = attr[1]()
            else:
                self[attr[0]] = attr[1](value=kwargs[attr[0]])
        for attr in optional_attrs:
            if attr[0] not in kwargs:
                if bool():
                    self[attr[0]] = attr[1]()
            else:
                if kwargs[attr[0]] != None:
                    self[attr[0]] = attr[1](value=kwargs[attr[0]])

class Time(builtins.int):
    """Random Time, which is a signed 64-bit integer representing seconds since
    the Unix epoch."""
    def __new__(cls, **kwargs):
        if 'value' not in kwargs:
            value = random.getrandbits(63)
        else:
            value = decimal_value = max(0, min(builtins.int(kwargs['value']), (2 ** 63) - 1))
        return super().__new__(cls, value)

class Snowflake(str):
    """Random 64-bit unsigned integer, represented as a 13-character base 36
    string."""
    def __new__(cls, **kwargs):
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyz' # For base conversion
        if 'value' not in kwargs:
            decimal_value = random.getrandbits(64) # Random unsigned 64-bit int
        else:
            try:
                decimal_value = max(0, min(builtins.int(kwargs['value'], 36), (2 ** 64) - 1))
            except TypeError:
                decimal_value = max(0, min(builtins.int(kwargs['value']), (2 ** 64) - 1))
        value = ''
        while len(value) < 13 or decimal_value > 0:
            decimal_value, i = divmod(decimal_value, len(alphabet))
            value = alphabet[i] + value
        return super().__new__(cls, value)

class UserID(str):
    """Random UserID, unless specified."""
    def __new__(cls, **kwargs):
        possible_values = {'agent': lambda: 'agent:' + string(length=12),
        'account': lambda: 'account:' + Snowflake(),
        'agent:': lambda: 'agent:' + string(length=12),
        'account:': lambda: 'account:' + Snowflake()}
        possible_prefixes = ('agent:', 'account:')
        validators = {'agent:': lambda x: len(str(x)) > (len('agent:') + 1), 'account:': lambda x: True}
        sanitizers = {'agent:': lambda x: str(x), 'account:': lambda x: Snowflake(value=x)}
        if 'value' not in kwargs:
            if 'prefix' not in kwargs:
                value = random.choice(tuple(possible_values.values()))()
            else:
                if kwargs['prefix'] not in possible_values.keys():
                    raise SyntaxError('invalid prefix for UserID')
                else:
                    value = possible_values[kwargs['prefix']]()
        else:
            value = str(kwargs['value'])
            validated = False
            for prefix in possible_prefixes:
                if value.lower().startswith(prefix):
                    try:
                        if validators[prefix](value):
                            value = prefix + sanitizers[prefix](value[len(prefix):])
                            validated = True
                            break
                    except:
                        pass
            if not validated:
                raise SyntaxError('invalid UserID')
        return super().__new__(cls, value)
