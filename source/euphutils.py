import re

class EuphUtils:
    def mention(nick):
        return '@' + ''.join(re.split(r'\s', nick))

    def mention_regex(nick):
        return re.compile(r'((?<=\s)|^)' + re.escape(EuphUtils.mention(nick)) + r'(\b|$|(?=\s))', re.IGNORECASE + re.MULTILINE)

    def command(name, nickname=None, match_string=None):
        if not nickname:
            return re.compile(name + r'\b\s*(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        return re.compile(name + r'\s+' + re.escape(EuphUtils.mention(nickname)) + r'(?:\b|$|(?=\s))\s*(.*)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
