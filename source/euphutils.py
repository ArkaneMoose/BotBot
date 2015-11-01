import re
import time

class EuphUtils:
    @classmethod
    def mention(cls, nick):
        return '@' + ''.join(re.split(r'\s', nick))

    @classmethod
    def mention_regex(cls, nick):
        return re.compile(r'((?<=\s)|^)' + re.escape(cls.mention(nick)) + r'(\b|$|(?=\s))', re.IGNORECASE + re.MULTILINE)

    @classmethod
    def command(cls, name, nickname=None, match_string=None):
        if nickname == '':
            return re.compile(name + r'\b\s*(?!@\S+)(\S.*|$)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        elif not nickname:
            return re.compile(name + r'\b\s*(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        return re.compile(name + r'\s+' + re.escape(cls.mention(nickname)) + r'(?:\b|$|(?=\s))\s*(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)

    @classmethod
    def uptime_utc(cls, start_time):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start_time))

    @classmethod
    def uptime_dhms(cls, start_time):
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

    @classmethod
    def uptime_str(cls, start_time):
        return '/me has been up since ' + cls.uptime_utc(start_time) + ' UTC (' + cls.uptime_dhms(start_time) + ')'
