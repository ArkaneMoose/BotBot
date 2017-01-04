from botbot.euphutils import EuphUtils
from botbot.botparser import Parser
from botbot.botbotbot import BotBotBot

import euphoria as eu
import threading

class BotCollection(eu.execgroup.ExecGroup):
    def __init__(self, botbot):
        super().__init__(autostop=False)

        self.botbot = botbot
        self.bots = self.execs

    def is_bot(self, agent_id):
        if self.botbot and self.botbot.agent_id == agent_id:
            return True
        for bot in self.bots:
            if bot.agent_id == agent_id:
                return True
        return False

    def get_description(self, bot=None):
        if not bot:
            if len(self.bots) == 0:
                return '(None)'
            return '\n'.join(map(self.get_description, self.bots))
        return EuphUtils.mention(bot.nickname) + ' (created by "' + bot.creator + '")' + ('' if self.botbot and self.botbot.room_name == bot.room_name else (' (in &' + bot.room_name.lower() + ')')) + (' (paused)' if bot.paused else '')

    def get_numberofrunningbots(self):
        return str(len(self.bots))
   
    def killall(self, announce=True, delete_file=True):
        while len(self.bots) > 0:
            self.bots[0].kill(announce=announce, delete_file=delete_file)

    def remove(self, bot):
        try:
            self.bots.remove(bot)
        except ValueError:
            pass

    def create(self, nickname, room_name, password, creator, code, paused=False, pause_text='', uuid=None, variables=None):
        if uuid:
            for bot in self.bots:
                if bot.uuid == uuid:
                    raise ValueError('bot with specified UUID already exists')
        bot = BotBotBot(room_name, password, nickname, creator, Parser(code), self, paused=paused, pause_text=pause_text, uuid=uuid, variables=variables)
        self.add(bot)
        return bot

    def retrieve(self, nickname=None, mention_name=None, room_name=None):
        # Ideally, this method should be accessible from the front-end, i.e.
        # through the !list command in Euphoria.
        matching_bots = []
        for bot in self.bots:
            if nickname and bot.nickname.lower() != nickname.lower():
                continue
            if mention_name and EuphUtils.mention(bot.nickname).lower() != EuphUtils.mention(mention_name).lower():
                continue
            if room_name and bot.room_name.lower() != room_name.lower():
                continue
            matching_bots.append(bot)
        return matching_bots

    def interbot(self, mention_name, target_room_name, message, sender, send_time, sender_agent_id, room_name):
        for bot in self.bots:
            if EuphUtils.mention(bot.nickname).lower() == EuphUtils.mention(mention_name).lower() and (not target_room_name or bot.room_name.lower() == target_room_name.lower()):
                bot.recv_message(message, None, None, sender, sender_agent_id, send_time, room_name)
