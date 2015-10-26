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

    def killall(self, announce=True):
        while len(self.bots) > 0:
            self.bots[0].kill(announce)

    def remove(self, bot):
        try:
            self.bots.remove(bot)
        except ValueError:
            pass

    def create(self, nickname, room_name, password, creator, code):
        bot = BotBotBot(room_name, password, nickname, creator, Parser(code), self)
        self.add(bot)
        return bot

    def interbot(self, nickname, target_room_name, message, sender, send_time, sender_agent_id, room_name):
        for bot in self.bots:
            if bot.nickname.lower() == nickname.lower() and (not target_room_name or bot.room_name.lower() == target_room_name.lower()):
                bot.recv_message(message, None, None, sender, sender_agent_id, send_time, room_name)
