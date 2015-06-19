from euphutils import EuphUtils
from botparser import Parser
import euphoria as eu
import threading

class BotCollection:
    botbot = None
    bots = []

    def is_bot(agent_id):
        if BotCollection.botbot and BotCollection.botbot.agent_id == agent_id:
            return True
        for bot in BotCollection.bots:
            if bot.agent_id == agent_id:
                return True
        return False

    def get_description(bot=None):
        if not bot:
            if len(BotCollection.bots) == 0:
                return '(None)'
            return '\n'.join(map(BotCollection.get_description, BotCollection.bots))
        return EuphUtils.mention(bot.nickname) + ' (created by "' + bot.creator + '")' + ('' if BotCollection.botbot and BotCollection.botbot.room_name == bot.room_name else (' (in &' + bot.room_name.lower() + ')')) + (' (paused)' if bot.paused else '')

    def killall(announce=True):
        for bot in BotCollection.bots:
            bot.kill(announce)

    def remove(bot):
        try:
            BotCollection.bots.remove(bot)
        except ValueError:
            pass

    def create(nickname, room_name, password, creator, code):
        bot = BotBotBot(room_name, password, nickname, creator, Parser(code))
        BotCollection.bots.append(bot)
        threading.Thread(target=bot.run).start()

    def interbot(nickname, target_room_name, message, sender, send_time, sender_agent_id, room_name):
        for bot in BotCollection.bots:
            if bot.nickname.lower() == nickname.lower() and (not target_room_name or bot.room_name.lower() == target_room_name.lower()):
                bot.recv_message(message, None, None, sender, sender_agent_id, send_time, room_name)

from botbotbot import BotBotBot
