import unittest
import unittest.mock
import botbot.botbot
import tests.sample_data as sample_data
import random

class TestBotBot(unittest.TestCase):

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botbot.Snapshot')
    @unittest.mock.patch('botbot.botbot.log')
    def test_snapshot_checks(self, mock_class_1, mock_class_2, mock_class_3):
        """BotBot must not call Snapshot.load_current, Snapshot.load, or Snapshot.create if Snapshot.is_enabled() returns False."""
        mock_class_2.is_enabled.return_value = False
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.ready()
        message = sample_data.Message(content='!save @BotBot', truncated=None)
        instance.handle_chat(message)
        message = sample_data.Message(content='!load @BotBot test.tar.gz', truncated=None)
        instance.handle_chat(message)
        mock_class_2.is_enabled.assert_called_with()
        mock_class_2.load_current.assert_not_called()
        mock_class_2.load.assert_not_called()
        mock_class_2.create.assert_not_called()

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botbot.Snapshot')
    @unittest.mock.patch('botbot.botbot.log')
    def test_load_once(self, mock_class_1, mock_class_2, mock_class_3):
        """BotBot must call Snapshot.load_current exactly once per run."""
        mock_class_2.is_enabled.return_value = True
        mock_class_2.load_current.return_value = []
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.ready()
        instance.cleanup()
        instance.ready()
        mock_class_2.load_current.assert_called_once_with(unittest.mock.ANY)

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_ignore_messages(self, mock_class_1, mock_class_2):
        """BotBot must ignore truncated messages, messages that are from its own bots, and messages that are not commands."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.send_chat = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!ping', truncated=True)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()
        mock_class_2.return_value.is_bot.return_value = True
        message = sample_data.Message(content='!ping', truncated=None)
        instance.send_chat.assert_not_called()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='ping', truncated=None)
        instance.send_chat.assert_not_called()
        mock_class_2.return_value.is_bot.return_value = False

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_ping(self, mock_class_1, mock_class_2):
        """BotBot must respond to general and specific pings, but not to specific pings intended for another bot."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.send_chat = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!ping', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)
        instance.send_chat.reset_mock()
        message = sample_data.Message(content='!ping @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)
        instance.send_chat.reset_mock()
        message = sample_data.Message(content='!ping @BotBotTest2', truncated=None)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_uptime(self, mock_class_1, mock_class_2):
        """BotBot must respond to the specific !uptime command."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.send_chat = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!uptime @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_list(self, mock_class_1, mock_class_2):
        """BotBot must respond to the specific !list command."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.send_chat = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!list @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_list(self, mock_class_1, mock_class_2):
        """BotBot must respond to the specific !list command."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.send_chat = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!list @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_short_help(self, mock_class_1, mock_class_2):
        """BotBot must respond to the general !help command when short_help_text is provided."""
        short_help_text = sample_data.string(length=random.randint(1, 255))
        instance = botbot.botbot.BotBot('testing', None, 'BotBot', short_help_text=short_help_text)
        instance.send_chat = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!help', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_help(self, mock_class_1, mock_class_2):
        """BotBot must respond to the specific !help command when help_text is provided, but not to specific !help commands intended for other bots."""
        short_help_text = sample_data.string(length=random.randint(1, 255))
        help_text = sample_data.string(length=random.randint(1, 255))
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test', short_help_text=short_help_text, help_text=help_text)
        instance.send_chat = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!help @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)
        instance.send_chat.reset_mock()
        message = sample_data.Message(content='!help @BotBotTest2', truncated=None)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_killall(self, mock_class_1, mock_class_2):
        """BotBot must kill all bots when the specific !killall command is issued."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.send_chat = unittest.mock.MagicMock()
        instance.bots.killall = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        message = sample_data.Message(content='!killall @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.bots.killall.called)

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.botcollection.BotCollection')
    def test_createbot(self, mock_class_1, mock_class_2):
        """BotBot must correctly create a bot when the !createbot command is issued and fail gracefully if the bot's code is invalid."""
        instance = botbot.botbot.BotBot('testing', 'password', 'BotBot')
        instance.send_chat = unittest.mock.MagicMock()
        instance.bots.create = unittest.mock.MagicMock()
        mock_class_2.return_value.is_bot.return_value = False
        code = sample_data.string(length=random.randint(1, 255))
        message = sample_data.Message(content='!createbot &test @TestBot ' + code, truncated=None)
        sender = message['sender']
        instance.handle_chat(message)
        instance.bots.create.assert_called_once_with('TestBot', 'test', None, sender['name'], code)
        instance.bots.create.reset_mock()
        code = sample_data.string(length=random.randint(1, 255))
        message = sample_data.Message(content='!createbot @TestBot ' + code, truncated=None)
        sender = message['sender']
        instance.handle_chat(message)
        instance.bots.create.assert_called_once_with('TestBot', 'testing', 'password', sender['name'], code)
        instance.bots.create.reset_mock()
        try:
            instance.bots.create.side_effect = Exception()
            code = sample_data.string(length=random.randint(1, 255))
            message = sample_data.Message(content='!createbot @TestBot ' + code, truncated=None)
            sender = message['sender']
            instance.handle_chat(message)
        except:
            self.fail('Exception not caught when creating a bot with an error.')

if __name__ == '__main__':
    unittest.main()
