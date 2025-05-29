'''this is the testing file for ds_messenger'''
import json
import socket
import unittest
from unittest.mock import MagicMock, patch
from ds_messenger import DirectMessenger, DirectMessage


class TestDirectMessage(unittest.TestCase):
    """Tests for DirectMessage class"""
    def test_direct_message_init(self) -> None:
        '''tests if the directmessage class is creating objects correctly'''
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

    def test_get_recipient(self) -> None:
        '''tests if get recipent works correctly'''
        msg = DirectMessage(recipient="bro", message="Hi")
        self.assertEqual(msg.get_recipient(), "bro")

    def test_get_message(self) -> None:
        '''tests if get message works correctly'''
        msg = DirectMessage(recipient="kimi", message="Hi")
        self.assertEqual(msg.get_message(), "Hi")


class TestDirectMessenger(unittest.TestCase):
    """Tests for DirectMessenger class"""
    def setUp(self) -> None:
        """Create a test messenger instance before each test"""
        self.messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')

    @patch('socket.socket')
    def test_init_connection_success(self, mock_socket) -> None:
        """Test successful connection during initialization"""
        mock_socket.return_value.connect.return_value = None
        mock_file = MagicMock()
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "yay",
                "token": "test"
            }
        })
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNotNone(messenger.token)
        self.assertEqual(messenger.token, "test")

    @patch('socket.socket')
    def test_init_connection_failure(self, mock_socket) -> None:
        """Test failed connection during initialization"""

        mock_file = mock_socket.return_value.makefile
        mock_file.side_effect = socket.timeout("Timeout")

        mock_file = MagicMock()
        mock_file.readline.return_value = None
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')

        self.assertIsNone(messenger.token)

    @patch('socket.socket')
    def test_send_message_success(self, mock_socket) -> None:
        """Test successful message sending"""
        mock_file = MagicMock()
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "yay",
                "token": "test"
            }
        })
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')

        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "Message sent"
            }
        })

        result = messenger.send("Hello", "alice")
        self.assertTrue(result)

    @patch('socket.socket')
    def test_send_message_failure(self, mock_socket) -> None:
        """Test failed message sending"""
        mock_socket.return_value.connect.side_effect = socket.timeout

        mock_file = MagicMock()
        mock_file.readline.return_value = None
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')

        result = messenger.send("Hello", "alice")
        self.assertFalse(result)

    @patch('socket.socket')
    def test_retrieve_all_messages(self, mock_socket) -> None:
        """Test retrieving all messages"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({
                "response": {
                    "type": "ok",
                    "message": "Success",
                    "token": "abc123"
                }
            }),
            json.dumps({
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
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].sender, "alice")

    @patch('socket.socket')
    def test_retrieve_new_messages(self, mock_socket) -> None:
        """Test retrieving new messages"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({
                "response": {
                    "type": "ok",
                    "message": "Success",
                    "token": "abc123"
                }
            }),
            json.dumps({
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
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_new()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "New message")

    @patch('socket.socket')
    def test_connection_error_handling(self, mock_socket) -> None:
        """Test connection error handling"""
        mock_file = mock_socket.return_value.makefile
        mock_file.side_effect = ConnectionError("Connection failed")

        # This will test both connection and error handling
        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNone(messenger.token)

        # Test sending message with failed connection
        result = messenger.send("Hello", "alice")
        self.assertFalse(result)

    @patch('socket.socket')
    def test_timeout_handling(self, mock_socket) -> None:
        """Test timeout handling"""
        mock_file = mock_socket.return_value.makefile
        mock_file.side_effect = socket.timeout("Timeout")

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNone(messenger.token)

        # Test retrieving messages with timeout
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 0)

    @patch('socket.socket')
    def test_empty_messages_response(self, mock_socket) -> None:
        """Test empty messages list response"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({
                "response": {
                    "type": "ok",
                    "message": "hiiii",
                    "token": "123"
                }
            }),
            json.dumps({
                "response": {
                    "type": "ok",
                    "messages": []
                }
            })
        ]
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 0)

    @patch('socket.socket')
    def test_failed_messages_retrieval(self, mock_socket) -> None:
        """Test failed messages retrieval"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            json.dumps({
                "response": {
                    "type": "ok",
                    "message": "hi",
                    "token": "example"
                }
            }),
            json.dumps({
                "response": {
                    "type": "error",
                    "message": "Failed to get messages"
                }
            })
        ]
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        messages = messenger.retrieve_all()
        self.assertEqual(len(messages), 0)

    @patch('socket.socket')
    def test_successful_authentication(self, mock_socket) -> None:
        """Test successful authentication"""

        mock_file = MagicMock()
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "Success",
                "token": "sample_token"
            }
        })
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')

        self.assertEqual(messenger.token, "sample_token")
        self.assertTrue(messenger.send("test", "user"))

    @patch('socket.socket')
    def test_failed_authentication(self, mock_socket) -> None:
        """Test failed authentication"""
        # Setup mock to return error response
        mock_file = MagicMock()
        mock_file.readline.return_value = json.dumps({
            "response": {
                "type": "error",
                "message": "doesn't work"
            }
        })
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNone(messenger.token)
        self.assertFalse(messenger.send("hello", "user"))

    @patch('socket.socket')
    def test_no_authentication_response(self, mock_socket) -> None:
        """Test when server doesn't respond to authentication"""
        mock_file = MagicMock()
        mock_file.readline.return_value = None
        sock = mock_socket.return_value
        sock.makefile.return_value.__enter__.return_value = mock_file

        messenger = DirectMessenger(
            dsuserver='127.0.0.1', username='bob', password='123')
        self.assertIsNone(messenger.token)


if __name__ == '__main__':
    unittest.main()
