import unittest
import unittest.mock
import botbot.longmessage_room
import tests.sample_data as sample_data

class TestLongMessageRoom(unittest.TestCase):

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_callback_registration(self, mock_class):
        """LongMessageRoom must register for send-event and get-message-reply callbacks."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        calls = [unittest.mock.call('send-event', unittest.mock.ANY), unittest.mock.call('get-message-reply', unittest.mock.ANY)]
        instance.connection.add_callback.assert_has_calls(calls, any_order=True)

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_request_full_message(self, mock_class):
        """LongMessageRoom must send get-message packet if packet with truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=True)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        instance.connection.send_packet.assert_called_with('get-message', {'id': message['id']})

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_dont_request_full_message(self, mock_class):
        """LongMessageRoom must not send packet if packet without truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        instance.connection.send_packet.assert_not_called()

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.longmessage_room.LongMessageRoom.handle_chat')
    def test_handle_getmessagereply(self, mock_class_1, mock_class_2):
        """LongMessageRoom must pass message to handle_chat if packet without truncated message is received."""
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.handle_getmessagereply({'type': sample_data.PacketType(value='get-message-reply'), 'data': message})
        instance.handle_chat.assert_called_with(message)

if __name__ == '__main__':
    unittest.main()
