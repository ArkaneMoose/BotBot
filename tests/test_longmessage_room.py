import unittest
import botbot.longmessage_room
import tests.sample_data as sample_data
try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestLongMessageRoom(unittest.TestCase):

    @mock.patch('euphoria.room.connection')
    def test_callback_registration(self, mock_connection):
        """LongMessageRoom must register for send-event and get-message-reply callbacks."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        calls = [mock.call('send-event', mock.ANY), mock.call('get-message-reply', mock.ANY)]
        instance.connection.add_callback.assert_has_calls(calls, any_order=True)

    @mock.patch('euphoria.room.connection')
    def test_request_full_message(self, mock_connection):
        """LongMessageRoom must send get-message packet if packet with truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=True)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        instance.connection.send_packet.assert_called_with('get-message', {'id': message['id']})

    @mock.patch('euphoria.room.connection')
    def test_dont_request_full_message(self, mock_connection):
        """LongMessageRoom must not send packet if packet without truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        instance.connection.send_packet.assert_not_called()

    @mock.patch('euphoria.room.connection')
    @mock.patch('botbot.longmessage_room.LongMessageRoom.handle_chat')
    def test_handle_getmessagereply(self, mock_handle_chat, mock_connection):
        """LongMessageRoom must pass message to handle_chat if packet without truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.handle_getmessagereply({'type': sample_data.PacketType(value='get-message-reply'), 'data': message})
        instance.handle_chat.assert_called_with(message)

if __name__ == '__main__':
    unittest.main()
