import re
import time

class EuphUtils:
    def mention(nick):
        return '@' + ''.join(re.split(r'\s', nick))

    def mention_regex(nick):
        return re.compile(r'((?<=\s)|^)' + re.escape(EuphUtils.mention(nick)) + r'(\b|$|(?=\s))', re.IGNORECASE + re.MULTILINE)

    def command(name, nickname=None, match_string=None):
        if nickname == '':
            return re.compile(name + r'\b\s*(?!@\S+)(\S.*|$)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        elif not nickname:
            return re.compile(name + r'\b\s*(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        return re.compile(name + r'\s+' + re.escape(EuphUtils.mention(nickname)) + r'(?:\b|$|(?=\s))\s*(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)

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
        return '/me has been up since ' + EuphUtils.uptime_utc(start_time) + ' UTC (' + EuphUtils.uptime_dhms(start_time) + ')'
