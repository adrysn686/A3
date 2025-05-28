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
    def test_init_connection_success(self, mock_socket):
        """Test successful connection during initialization"""
        mock_socket.return_value.connect.return_value = None
        mock_file = MagicMock()
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "Success",
                "token": "abc123"
            }
        })
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNotNone(messenger.token)
        self.assertEqual(messenger.token, "abc123")

    @patch('socket.socket')
    def test_init_connection_failure(self, mock_socket):
        """Test failed connection during initialization"""
        # Mock connection to fail
        mock_socket.return_value.connect.side_effect = socket.timeout

        # Mock makefile to return None for failed connection
        mock_file = MagicMock()
        mock_file.readline.return_value = None
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file

        # Create messenger - should handle connection failure gracefully
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')

        # Verify authentication failed
        self.assertIsNone(messenger.token)


    @patch('socket.socket')
    def test_send_message_success(self, mock_socket):
        """Test successful message sending"""
        # Mock successful authentication
        mock_file = MagicMock()
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "Success",
                "token": "abc123"
            }
        })
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        
        # Mock message sending
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "Message sent"
            }
        })
        
        result = messenger.send("Hello", "alice")
        self.assertTrue(result)

    @patch('socket.socket')
    def test_send_message_failure(self, mock_socket):
        """Test failed message sending"""
        # Mock connection to fail
        mock_socket.return_value.connect.side_effect = socket.timeout
        
        # Mock makefile to return None for failed connection
        mock_file = MagicMock()
        mock_file.readline.return_value = None
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        # Create messenger - should handle connection failure gracefully
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        
        # Test sending message
        result = messenger.send("Hello", "alice")
        self.assertFalse(result)

    @patch('socket.socket')
    def test_retrieve_all_messages(self, mock_socket):
        """Test retrieving all messages"""
        # Mock successful authentication
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({  # Auth response
                "response": {
                    "type": "ok",
                    "message": "Success",
                    "token": "abc123"
                }
            }),
            json.dumps({  # Retrieve response
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
            })
        ]
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].sender, "alice")

    @patch('socket.socket')
    def test_retrieve_new_messages(self, mock_socket):
        """Test retrieving new messages"""
        # Mock successful authentication
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({  # Auth response
                "response": {
                    "type": "ok",
                    "message": "Success",
                    "token": "abc123"
                }
            }),
            json.dumps({  # Retrieve response
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
            })
        ]
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_new()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "New message")

    @patch('socket.socket')
    def test_connection_error_handling(self, mock_socket):
        """Test connection error handling"""
        mock_socket.return_value.makefile.side_effect = ConnectionError("Connection failed")
        
        # This will test both connection and error handling
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNone(messenger.token)
        
        # Test sending message with failed connection
        result = messenger.send("Hello", "alice")
        self.assertFalse(result)

    @patch('socket.socket')
    def test_timeout_handling(self, mock_socket):
        """Test timeout handling"""
        mock_socket.return_value.makefile.side_effect = socket.timeout("Timeout")
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNone(messenger.token)
        
        # Test retrieving messages with timeout
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 0)

    @patch('socket.socket')
    def test_empty_messages_response(self, mock_socket):
        """Test empty messages list response"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({  # Auth response
                "response": {
                    "type": "ok",
                    "message": "Success",
                    "token": "abc123"
                }
            }),
            json.dumps({  # Empty messages response
                "response": {
                    "type": "ok",
                    "messages": []
                }
            })
        ]
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 0)

    @patch('socket.socket')
    def test_failed_messages_retrieval(self, mock_socket):
        """Test failed messages retrieval"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({  # Auth response
                "response": {
                    "type": "ok",
                    "message": "Success",
                    "token": "abc123"
                }
            }),
            json.dumps({  # Error response
                "response": {
                    "type": "error",
                    "message": "Failed to retrieve messages"
                }
            })
        ]
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 0)
    
    @patch('socket.socket')
    def test_init_invalid_auth_response(self, mock_socket):
        """Test initialization with invalid auth response"""
        # Mock successful connection but invalid response
        mock_file = MagicMock()
        mock_file.readline.return_value = "invalid json"
        mock_socket.return_value.makefile.return_value.__enter__.return_value = mock_file
        
        messenger = DirectMessenger(dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNone(messenger.token)

if __name__ == '__main__':
    unittest.main()