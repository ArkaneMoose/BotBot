import unittest
import unittest.mock
import botbot.agentid_room
import tests.sample_data as sample_data
import random

class TestAgentIdRoom(unittest.TestCase):

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_callback_registration(self, mock_class):
        instance = botbot.agentid_room.AgentIdRoom('testing')
        expected = ('nick-reply', 'send-reply')
        for callback_type in expected:
            self.assertTrue(((callback_type, unittest.mock.ANY), {}) in instance.connection.add_callback.call_args_list)

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_handle_nickreply_packet(self, mock_class):
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_nickreply({'type': 'nick-reply', 'data': {'id': user_id}})
        self.assertEqual(instance.agent_id, user_id)

    @unittest.mock.patch('euphoria.connection.Connection')
    def test_handle_error_nickreply_packet(self, mock_class):
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_nickreply({'type': 'nick-reply', 'data': {'id': user_id}})
        instance.handle_nickreply({'type': 'nick-reply', 'error': sample_data.string()})
        self.assertEqual(instance.agent_id, user_id)

    @unittest.mock.patch('botbot.agentid_room.room.Room')
    def test_handle_sendreply_packet(self, mock_class):
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_sendreply({'type': 'send-reply', 'data': {'sender': {'id': user_id, 'name': sample_data.string(length=random.randint(1, 36))}}})
        self.assertEqual(instance.agent_id, user_id)

    @unittest.mock.patch('botbot.agentid_room.room.Room')
    def test_handle_error_sendreply_packet(self, mock_class):
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_sendreply({'type': 'send-reply', 'data': {'sender': {'id': user_id, 'name': sample_data.string(length=random.randint(1, 36))}}})
        instance.handle_sendreply({'type': 'send-reply', 'error': sample_data.string()})
        self.assertEqual(instance.agent_id, user_id)

if __name__ == '__main__':
    unittest.main()
