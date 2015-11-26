import unittest
import botbot.agentid_room
import tests.sample_data as sample_data
import random
try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestAgentIdRoom(unittest.TestCase):

    @mock.patch('euphoria.room.connection')
    def test_callback_registration(self, mock_connection):
        """AgentIdRoom must register for nick-reply and send-reply callbacks."""
        instance = botbot.agentid_room.AgentIdRoom('testing')
        calls = [mock.call('nick-reply', mock.ANY), mock.call('send-reply', mock.ANY)]
        instance.connection.add_callback.assert_has_calls(calls, any_order=True)

    @mock.patch('euphoria.room.connection')
    def test_handle_nickreply_packet(self, mock_connection):
        """AgentIdRoom must set agent ID if received through nick-reply packet."""
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_nickreply({'type': 'nick-reply', 'data': {'id': user_id}})
        self.assertEqual(instance.agent_id, user_id)

    @mock.patch('euphoria.room.connection')
    def test_handle_error_nickreply_packet(self, mock_connection):
        """AgentIdRoom must not reset agent ID or throw error if nick-reply packet without agent ID is received."""
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_nickreply({'type': 'nick-reply', 'data': {'id': user_id}})
        instance.handle_nickreply({'type': 'nick-reply', 'error': sample_data.string()})
        self.assertEqual(instance.agent_id, user_id)

    @mock.patch('euphoria.room.connection')
    def test_handle_sendreply_packet(self, mock_connection):
        """AgentIdRoom must set agent ID if received through send-reply packet."""
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_sendreply({'type': 'send-reply', 'data': {'sender': {'id': user_id, 'name': sample_data.string(length=random.randint(1, 36))}}})
        self.assertEqual(instance.agent_id, user_id)

    @mock.patch('euphoria.room.connection')
    def test_handle_error_sendreply_packet(self, mock_connection):
        """AgentIdRoom must not reset agent ID or throw error if send-reply packet without agent ID is received."""
        instance = botbot.agentid_room.AgentIdRoom('testing')
        user_id = sample_data.UserID()
        instance.handle_sendreply({'type': 'send-reply', 'data': {'sender': {'id': user_id, 'name': sample_data.string(length=random.randint(1, 36))}}})
        instance.handle_sendreply({'type': 'send-reply', 'error': sample_data.string()})
        self.assertEqual(instance.agent_id, user_id)

if __name__ == '__main__':
    unittest.main()
