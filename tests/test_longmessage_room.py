import unittest
import botbot.longmessage_room
import tests.sample_data as sample_data
try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestLongMessageRoom(unittest.TestCase):

    @mock.patch('euphoria.connection.Connection')
    def test_callback_registration(self, mock_class):
        """LongMessageRoom must register for send-event and get-message-reply callbacks."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        calls = [mock.call('send-event', mock.ANY), mock.call('get-message-reply', mock.ANY)]
        instance.connection.add_callback.assert_has_calls(calls, any_order=True)

    @mock.patch('euphoria.connection.Connection')
    def test_request_full_message(self, mock_class):
        """LongMessageRoom must send get-message packet if packet with truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=True)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        instance.connection.send_packet.assert_called_with('get-message', {'id': message['id']})

    @mock.patch('euphoria.connection.Connection')
    def test_dont_request_full_message(self, mock_class):
        """LongMessageRoom must not send packet if packet without truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        instance.connection.send_packet.assert_not_called()

    @mock.patch('euphoria.connection.Connection')
    @mock.patch('botbot.longmessage_room.LongMessageRoom.handle_chat')
    def test_handle_getmessagereply(self, mock_class_1, mock_class_2):
        """LongMessageRoom must pass message to handle_chat if packet without truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.handle_getmessagereply({'type': sample_data.PacketType(value='get-message-reply'), 'data': message})
        instance.handle_chat.assert_called_with(message)

if __name__ == '__main__':
    unittest.main()
