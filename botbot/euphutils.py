import re
import time
import urllib.request, urllib.error

def mention(nick):
    return '@' + ''.join(re.split(r'\s', nick))

def mention_regex(nick):
    return re.compile(r'((?<=\s)|^)' + re.escape(mention(nick)) + r'(\b|$|(?=\s))', re.IGNORECASE + re.MULTILINE)

def command(name, nickname=None, match_string=None):
    if nickname == '':
        return re.compile(name + r'\s*$', re.IGNORECASE + re.DOTALL + re.MULTILINE)
    elif not nickname:
        return re.compile(name + r'(?:$|\s+)(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
    return re.compile(name + r'\s+' + re.escape(mention(nickname)) + r'(?:$|\s+)(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)

def uptime_utc(start_time):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start_time))

def uptime_dhms(start_time):
    # Credit to jedevc for this function.
    # This has been slightly modified from the original.
    # https://github.com/jedevc/EuPy/blob/3918918a7c03f2e8933191566e0f1536487f6097/euphoria/utils.py#L57-L76
    m, s = divmod(time.time() - start_time, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d == 0 and h == 0 and m == 0:
        return "%ds" % s
    if d == 0 and h == 0:
        return "%dm %ds" % (m, s)
    if d == 0:
        return "%dh %dm %ds" % (h, m, s)
    return "%dd %dh %dm %ds" % (d, h, m, s)

def uptime_str(start_time):
    return '/me has been up since ' + uptime_utc(start_time) + ' UTC (' + uptime_dhms(start_time) + ')'

# HACK: more proper fix would be for EuPy to:
#   a) distinguish 404s from other errors and
#   b) pass those errors up the chain somehow
def assert_room_exists(room):
    try:
        req = urllib.request.Request(method='HEAD',
            url=f'https://euphoria.leet.nu/room/{room}/ws')
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if e.code == 400:
            return True
        # very fragile... could break if e.g. a valid room is redirected to its web page
        raise e
