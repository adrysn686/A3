import json
import socket
import unittest
from unittest.mock import MagicMock, patch
from ds_messenger import DirectMessenger, DirectMessage

class TestDirectMessage(unittest.TestCase):
    """Tests for DirectMessage class"""
    def test_direct_message_creation(self):
        msg = DirectMessage(
            recipient="bob",
            message="Hello",
            sender="alice",
            timestamp="12:00"
        )
        self.assertEqual(msg.recipient, "bob")
        self.assertEqual(msg.message, "Hello")
        self.assertEqual(msg.sender, "alice")
        self.assertEqual(msg.timestamp, "12:00")

class TestDirectMessenger(unittest.TestCase):
    """Tests for DirectMessenger class"""
    def setUp(self):
        """Create a test messenger instance before each test"""
        self.messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')

    @patch('socket.socket')
    def test_connect_success(self, mock_socket):
        """Test successful connection"""
        mock_socket.return_value.connect.return_value = None
        result = self.messenger._DirectMessenger__connect()
        self.assertTrue(result)
        mock_socket.return_value.connect.assert_called_once_with(('127.0.0.1', 3001))

    @patch('socket.socket')
    def test_connect_failure(self, mock_socket):
        """Test failed connection"""
        mock_socket.return_value.connect.side_effect = socket.timeout
        result = self.messenger._DirectMessenger__connect()
        self.assertFalse(result)

    @patch('ds_messenger.DirectMessenger._DirectMessenger__send_command')
    def test_authenticate_success(self, mock_send):
        """Test successful authentication"""
        mock_response = {
            "response": {
                "type": "ok",
                "message": "Success",
                "token": "abc123"
            }
        }
        mock_send.return_value = json.dumps(mock_response)
        
        result = self.messenger._DirectMessenger__authenticate()
        self.assertTrue(result)
        self.assertEqual(self.messenger.token, "abc123")

    @patch('ds_messenger.extract_json')
    @patch('ds_messenger.DirectMessenger._DirectMessenger__send_command')
    def test_authenticate_failure(self, mock_send, mock_extract):
        """Test failed authentication"""
        # Set up mocks before instantiation
        mock_send.return_value = 'mock_response'
        mock_extract.return_value.type = "error"
        mock_extract.return_value.message = "Invalid credentials"
        
        # Create messenger with disabled auto-auth
        messenger = DirectMessenger(dsuserver=None, username=None, password=None)
        messenger.host = '127.0.0.1'
        messenger.username = 'bob'
        messenger.password = '123'
        
        # Now test authentication
        result = messenger._DirectMessenger__authenticate()
        self.assertFalse(result)
        self.assertIsNone(messenger.token)

    @patch('ds_messenger.DirectMessenger._DirectMessenger__send_command')
    def test_send_message_success(self, mock_send):
        """Test successful message sending"""
        self.messenger.token = "valid_token"
        mock_response = {
            "response": {
                "type": "ok",
                "message": "Message sent"
            }
        }
        mock_send.return_value = json.dumps(mock_response)
        
        result = self.messenger.send("Hello", "alice")
        self.assertTrue(result)

    @patch('ds_messenger.DirectMessenger._DirectMessenger__authenticate')
    def test_send_message_failure(self, mock_auth):
        """Test failed message sending"""
        mock_auth.return_value = False
        result = self.messenger.send("Hello", "alice")
        self.assertFalse(result)

    @patch('ds_messenger.DirectMessenger._DirectMessenger__send_command')
    def test_retrieve_all_messages(self, mock_send):
        """Test retrieving all messages"""
        self.messenger.token = "valid_token"
        mock_response = {
            "response": {
                "type": "ok",
                "messages": [
                    {
                        "from": "alice",
                        "message": "Hi",
                        "timestamp": "12:00",
                        "recipient": "bob"
                    }
                ]
            }
        }
        mock_send.return_value = json.dumps(mock_response)
        
        messages = self.messenger.retrieve_all()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].sender, "alice")

    @patch('socket.socket')
    def test_send_command_success(self, mock_socket):
        """Test successful command sending"""
        # Set up mock file response
        mock_file = MagicMock()
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "Command processed"
            }
        })
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        # Create messenger with disabled auto-auth
        messenger = DirectMessenger(dsuserver=None, username=None, password=None)
        messenger.socket = mock_socket.return_value
        
        # Test sending command
        response = messenger._DirectMessenger__send_command('{"test": "command"}')
        response_data = json.loads(response)
        self.assertEqual(response_data['response']['type'], "ok")
        mock_file.write.assert_called_once_with('{"test": "command"}\r\n')
    
    @patch('ds_messenger.DirectMessenger._DirectMessenger__send_command')
    def test_retrieve_new_messages(self, mock_send):
        """Test retrieving new messages"""
        self.messenger.token = "valid_token"
        mock_response = {
            "response": {
                "type": "ok",
                "messages": [
                    {
                        "from": "alice",
                        "message": "New message",
                        "timestamp": "12:05",
                        "recipient": "bob"
                    }
                ]
            }
        }
        mock_send.return_value = json.dumps(mock_response)
        
        messages = self.messenger.retrieve_new()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "New message")

    @patch('socket.socket')
    def test_send_command_connection_error(self, mock_socket):
        """Test send command with connection error"""
        mock_socket.return_value.makefile.side_effect = ConnectionError("Connection failed")
        
        messenger = DirectMessenger(dsuserver=None, username=None, password=None)
        messenger.socket = mock_socket.return_value
        
        response = messenger._DirectMessenger__send_command('{"test": "command"}')
        self.assertIsNone(response)
    
    @patch('socket.socket')
    def test_send_command_timeout(self, mock_socket):
        """Test send command with timeout"""
        mock_socket.return_value.makefile.side_effect = socket.timeout("Timeout")
        
        messenger = DirectMessenger(dsuserver=None, username=None, password=None)
        messenger.socket = mock_socket.return_value
        
        response = messenger._DirectMessenger__send_command('{"test": "command"}')
        self.assertIsNone(response)
    
    @patch('ds_messenger.DirectMessenger._DirectMessenger__send_command')
    def test_retrieve_empty_messages(self, mock_send):
        """Test retrieving empty messages list"""
        self.messenger.token = "valid_token"
        mock_response = {
            "response": {
                "type": "ok",
                "messages": []
            }
        }
        mock_send.return_value = json.dumps(mock_response)
        
        messages = self.messenger.retrieve_all()
        self.assertEqual(len(messages), 0)

    @patch('ds_messenger.DirectMessenger._DirectMessenger__send_command')
    def test_retrieve_messages_failure(self, mock_send):
        """Test failed message retrieval"""
        self.messenger.token = "valid_token"
        mock_response = {
            "response": {
                "type": "error",
                "message": "Failed to retrieve messages"
            }
        }
        mock_send.return_value = json.dumps(mock_response)
        
        messages = self.messenger.retrieve_all()
        self.assertEqual(len(messages), 0)

    @patch('ds_messenger.DirectMessenger._DirectMessenger__authenticate')
    def test_retrieve_messages_auth_failure(self, mock_auth):
        """Test message retrieval with failed authentication"""
        mock_auth.return_value = False
        messages = self.messenger.retrieve_all()
        self.assertEqual(len(messages), 0)
    
if __name__ == '__main__':
    unittest.main()