import unittest
import botbot.botbot
import tests.sample_data as sample_data
import random
try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestBotBot(unittest.TestCase):

    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.Snapshot')
    @mock.patch('botbot.botbot.log')
    def test_snapshot_checks(self, mock_log, mock_Snapshot, mock_connection):
        """BotBot must not call Snapshot.load_current, Snapshot.load, or Snapshot.create if Snapshot.is_enabled() returns False."""
        mock_Snapshot.is_enabled.return_value = False
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.ready()
        message = sample_data.Message(content='!save @BotBot', truncated=None)
        instance.handle_chat(message)
        message = sample_data.Message(content='!load @BotBot test.tar.gz', truncated=None)
        instance.handle_chat(message)
        mock_Snapshot.is_enabled.assert_called_with()
        mock_Snapshot.load_current.assert_not_called()
        mock_Snapshot.load.assert_not_called()
        mock_Snapshot.create.assert_not_called()

    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.Snapshot')
    @mock.patch('botbot.botbot.log')
    def test_load_once(self, mock_log, mock_Snapshot, mock_connection):
        """BotBot must call Snapshot.load_current exactly once per run."""
        mock_Snapshot.is_enabled.return_value = True
        mock_Snapshot.load_current.return_value = []
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.ready()
        instance.cleanup()
        instance.ready()
        mock_Snapshot.load_current.assert_called_once_with(instance.bots)

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_ignore_messages(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must ignore truncated messages, messages that are from its own bots, and messages that are not commands."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!ping', truncated=True)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()
        instance.bots.is_bot.return_value = True
        message = sample_data.Message(content='!ping', truncated=None)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='ping', truncated=None)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_ping(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must respond to general and specific pings, but not to specific pings intended for another bot."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!ping', truncated=None)
        instance.handle_chat(message)
        instance.send_chat.reset_mock()
        message = sample_data.Message(content='!ping @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)
        instance.send_chat.reset_mock()
        message = sample_data.Message(content='!ping @BotBotTest2', truncated=None)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_uptime(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must respond to the specific !uptime command."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!uptime @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_list(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must respond to the specific !list command."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!list @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_list(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must respond to the specific !list command."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!list @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_short_help(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must respond to the general !help command when short_help_text is provided."""
        short_help_text = sample_data.string(length=random.randint(1, 255))
        instance = botbot.botbot.BotBot('testing', None, 'BotBot', short_help_text=short_help_text)
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!help', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_help(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must respond to the specific !help command when help_text is provided, but not to specific !help commands intended for other bots."""
        short_help_text = sample_data.string(length=random.randint(1, 255))
        help_text = sample_data.string(length=random.randint(1, 255))
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test', short_help_text=short_help_text, help_text=help_text)
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!help @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.send_chat.called)
        instance.send_chat.reset_mock()
        message = sample_data.Message(content='!help @BotBotTest2', truncated=None)
        instance.handle_chat(message)
        instance.send_chat.assert_not_called()

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_killall(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must kill all bots when the specific !killall command is issued."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.bots.killall = mock.MagicMock()
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!killall @BotBotTest', truncated=None)
        instance.handle_chat(message)
        self.assertTrue(instance.bots.killall.called)

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_createbot(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must correctly create a bot when the !createbot command is issued and fail gracefully if the bot's code is invalid."""
        instance = botbot.botbot.BotBot('testing', 'password', 'BotBot')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!createbot &test @TestBot code', truncated=None)
        sender = message['sender']
        instance.handle_chat(message)
        instance.bots.create.assert_called_once_with('TestBot', 'test', None, sender['name'], 'code')
        instance.bots.create.reset_mock()
        message = sample_data.Message(content='!createbot @TestBot code', truncated=None)
        sender = message['sender']
        instance.handle_chat(message)
        instance.bots.create.assert_called_once_with('TestBot', 'testing', 'password', sender['name'], 'code')
        instance.bots.create.reset_mock()
        try:
            instance.bots.create.side_effect = Exception()
            message = sample_data.Message(content='!createbot @TestBot code', truncated=None)
            sender = message['sender']
            instance.handle_chat(message)
        except:
            self.fail('Exception not caught when creating a bot with an error.')

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_sendbot_onebot(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must correctly send a bot when the !sendbot command is issued when only one specified bot exists."""
        instance = botbot.botbot.BotBot('testing', 'password', 'BotBot')
        matching_bot = mock.MagicMock()
        matching_bot.nickname = 'TestBot'
        instance.bots.is_bot.return_value = False
        instance.bots.get_description.return_value = ''
        instance.bots.retrieve.return_value = [matching_bot]
        message = sample_data.Message(content='!sendbot &test @TestBot', truncated=None)
        instance.handle_chat(message)
        instance.bots.retrieve.assert_called_with(mention_name='TestBot')
        instance.bots.create.assert_called_once_with(matching_bot.nickname, 'test', None, matching_bot.creator, matching_bot.code_struct.parse_string)
        instance.bots.retrieve.reset_mock()
        instance.bots.create.reset_mock()
        message = sample_data.Message(content='!sendbot @TestBot', truncated=None)
        instance.handle_chat(message)
        instance.bots.retrieve.assert_called_with(mention_name='TestBot')
        instance.bots.create.assert_called_once_with(matching_bot.nickname, 'testing', 'password', matching_bot.creator, matching_bot.code_struct.parse_string)
        instance.bots.retrieve.reset_mock()
        instance.bots.create.reset_mock()
        message = sample_data.Message(content='!sendbot &test @TestBot 1', truncated=None)
        instance.handle_chat(message)
        instance.bots.retrieve.assert_called_with(mention_name='TestBot')
        instance.bots.create.assert_called_once_with(matching_bot.nickname, 'test', None, matching_bot.creator, matching_bot.code_struct.parse_string)
        instance.bots.retrieve.reset_mock()
        instance.bots.create.reset_mock()
        message = sample_data.Message(content='!sendbot @TestBot 2', truncated=None)
        try:
            instance.handle_chat(message)
            instance.bots.retrieve.assert_called_with(mention_name='TestBot')
            instance.bots.create.assert_not_called()
        except:
            self.fail('Exception not caught when !sendbot is issued with identifier that is out of range.')

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_sendbot_multibot(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must correctly send a bot when the !sendbot command is issued when more than one specified bot exists."""
        instance = botbot.botbot.BotBot('testing', 'password', 'BotBot')
        instance.bots.is_bot.return_value = False
        instance.bots.get_description.return_value = ''
        matching_bot_1 = mock.MagicMock()
        matching_bot_1.nickname = 'TestBot'
        matching_bot_2 = mock.MagicMock()
        matching_bot_2.nickname = 'TestBot'
        instance.bots.retrieve = mock.MagicMock(return_value=[matching_bot_1, matching_bot_2])
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!sendbot &test @TestBot', truncated=None)
        instance.handle_chat(message)
        instance.bots.retrieve.assert_called_with(mention_name='TestBot')
        instance.bots.create.assert_not_called()
        instance.bots.retrieve.reset_mock()
        instance.bots.create.reset_mock()
        message = sample_data.Message(content='!sendbot &test @TestBot 2', truncated=None)
        instance.handle_chat(message)
        instance.bots.retrieve.assert_called_with(mention_name='TestBot')
        instance.bots.create.assert_called_once_with(matching_bot_2.nickname, 'test', None, matching_bot_2.creator, matching_bot_2.code_struct.parse_string)

    @mock.patch('botbot.botbot.BotBot.send_chat')
    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.BotCollection')
    def test_sendbot_nobots(self, mock_BotCollection, mock_connection, mock_send_chat):
        """BotBot must correctly send a bot when the !sendbot command is issued when no specified bot exists."""
        instance = botbot.botbot.BotBot('testing', 'password', 'BotBot')
        instance.bots.is_bot.return_value = False
        instance.bots.get_description.return_value = ''
        instance.bots.retrieve.return_value = []
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!sendbot &test @TestBot', truncated=None)
        instance.handle_chat(message)
        instance.bots.retrieve.assert_called_with(mention_name='TestBot')
        instance.bots.create.assert_not_called()

    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.Snapshot')
    @mock.patch('botbot.botbot.BotCollection')
    def test_save(self, mock_BotCollection, mock_Snapshot, mock_connection):
        """BotBot must call Snapshot.create when the specific !save command is issued."""
        mock_Snapshot.is_enabled.return_value = True
        instance = botbot.botbot.BotBot('testing', None, 'BotBot Test')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!save @BotBotTest', truncated=None)
        instance.handle_chat(message)
        mock_Snapshot.create.assert_called_once_with(instance.bots)

    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.Snapshot')
    @mock.patch('botbot.botbot.BotCollection')
    def test_load(self, mock_BotCollection, mock_Snapshot, mock_connection):
        """BotBot must call Snapshot.load when the specific !load command is issued and refuse to do so if the filename is invalid."""
        mock_Snapshot.is_enabled.return_value = True
        mock_Snapshot.get_filepath.return_value = 'filepath'
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.bots.is_bot.return_value = False
        message = sample_data.Message(content='!load @BotBot latest', truncated=None)
        instance.handle_chat(message)
        mock_Snapshot.load.assert_called_with('filepath', instance.bots)
        mock_Snapshot.load.reset_mock()
        mock_Snapshot.get_filepath.return_value = None
        message = sample_data.Message(content='!load @BotBot invalid.tar.gz', truncated=None)
        instance.handle_chat(message)
        mock_Snapshot.load.assert_not_called()
        mock_Snapshot.load.reset_mock()
        mock_Snapshot.get_filepath.return_value = None
        message = sample_data.Message(content='!load @BotBot invalid', truncated=None)
        instance.handle_chat(message)
        mock_Snapshot.load.assert_not_called()

    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.botbot.Snapshot')
    @mock.patch('botbot.botbot.BotCollection')
    def test_restart(self, mock_BotCollection, mock_Snapshot, mock_connection):
        """BotBot must call self.quit when the specific !restart command is issued."""
        instance = botbot.botbot.BotBot('testing', None, 'BotBot')
        instance.bots.is_bot.return_value = False
        instance.quit = mock.MagicMock()
        message = sample_data.Message(content='!restart @BotBot latest', truncated=None)
        instance.handle_chat(message)
        instance.quit.assert_called_once_with()

if __name__ == '__main__':
    unittest.main()
