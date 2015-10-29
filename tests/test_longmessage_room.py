import unittest
import unittest.mock
import botbot.longmessage_room
import tests.sample_data as sample_data
import random

class TestLongMessageRoom(unittest.TestCase):

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_callback_registration(self, mock_class):
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        expected = ('send-event', 'get-message-reply')
        for callback_type in expected:
            self.assertTrue(((callback_type, unittest.mock.ANY), {}) in instance.connection.add_callback.call_args_list)

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_request_full_message(self, mock_class):
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=True)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        instance.connection.send_packet.assert_called_with('get-message', {'id': message['id']})

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_dont_request_full_message(self, mock_class):
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.request_full_message({'type': sample_data.PacketType(value='send-event'), 'data': message})
        self.assertFalse(instance.connection.send_packet.called)

    @unittest.mock.patch('euphoria.connection.Connection')
    @unittest.mock.patch('botbot.longmessage_room.LongMessageRoom.handle_chat')
    def test_handle_getmessagereply(self, mock_class_1, mock_class_2):
        instance = botbot.longmessage_room.LongMessageRoom('testing')
        message = sample_data.Message(truncated=None)
        instance.handle_getmessagereply({'type': sample_data.PacketType(value='get-message-reply'), 'data': message})
        instance.handle_chat.assert_called_with(message)

if __name__ == '__main__':
    unittest.main()
