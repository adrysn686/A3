import json
import socket
from unittest.mock import MagicMock, patch
from unittest import TestCase
import pytest
from ds_messenger import DirectMessenger, DirectMessage

class TestMessenger(TestCase):

    @pytest.fixture
    def mock_direct_messenger():
        """creates an object of DirectMessenger"""
        return DirectMessenger(dsuserver='127.0.0.1', username='bob', password = '123')

    @pytest.fixture
    def mock_direct_message():
        return DirectMessage(
                recipient="billy",
                message="Hello",
                sender="claire",
                timestamp="12:00"
            )

    @patch('socket.socket')
    def test_connect_working(mock_socket, mock_direct_messenger):
        mock_socket_instance = mock_socket.return_value
        mock_connect = mock_socket_instance.connect #this is when i'm calling the connect method

        mock_connect.return_value = True

        assert mock_direct_messenger.connect() is True
        mock_connect.assert_called_once_with(('127.0.0.1', 3001))

    @patch('socket.socket')
    def test_connect_failure(mock_socket, mock_direct_messenger):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.connect.side_effect = Exception("Connection failed")

        assert mock_direct_messenger.connect() is False

    @patch('ds_messenger.DirectMessenger._send_command')
    def test_authenticate_success(mock_send, mock_direct_messenger):
        """Test successful authentication."""
        mock_send.return_value = json.dumps({
            "response": {
                "type": "ok",
                "message": "Success",
                "token": "abc123"
            }
        })

        assert mock_direct_messenger.authenticate() is True
        assert mock_direct_messenger.token == "abc123"


    @patch('ds_messenger.DirectMessenger._send_command')
    def test_authenticate_failure(mock_send, mock_direct_messenger):
        """Test failed authentication."""
        mock_send.return_value = json.dumps({
            "response": {
                "type": "error",
                "message": "Invalid credentials"
            }
        })

        assert mock_direct_messenger.authenticate() is False
        assert mock_direct_messenger.token is None

    @patch('ds_messenger.DirectMessenger._send_command')
    @patch('ds_messenger.DirectMessenger.authenticate')
    def test_retrieve_all(mock_auth, mock_send, mock_direct_messenger):
        """Test retrieving all messages."""
        mock_auth.return_value = True
        mock_send.return_value = json.dumps({
            "response": {
                "type": "ok",
                "messages": [
                    {
                        "from": "user2", 
                        "message": "Hi", 
                        "timestamp": "12:00",
                        "recipient": "bob"
                    }
                ]
            }
        })

        messages = mock_direct_messenger.retrieve_all()
        assert len(messages) == 1
        assert messages[0].sender == "user2"

    @patch('ds_messenger.DirectMessenger.authenticate')
    @patch('ds_messenger.DirectMessenger._send_command')
    def test_retrieve_new(mock_send, mock_auth, mock_direct_messenger):
        """Test retrieving new messages."""
        mock_auth.return_value = True
        mock_send.return_value = json.dumps({
            "response": {
                "type": "ok",
                "messages": [
                    {
                        "from": "user3", 
                        "message": "New message", 
                        "timestamp": "12:05",
                        "recipient": "bob"
                    }
                ]
            }
        })

        messages = mock_direct_messenger.retrieve_new()
        assert len(messages) == 1
        assert messages[0].message == "New message"

    @patch('socket.socket')
    def test_send_command_success(mock_socket, mock_direct_messenger):
        """Test successful command send."""
        mock_socket_instance = mock_socket.return_value
        mock_file = MagicMock()
        mock_file.readline.return_value = '{"response": "ok"}'
        mock_socket_instance.makefile.return_value.__enter__.return_value = mock_file

        response = mock_direct_messenger._send_command('{"test": "command"}')
        assert response == '{"response": "ok"}'
        mock_file.write.assert_called_once_with('{"test": "command"}\r\n')


    def test_close_success(mock_direct_messenger):
        """Test closing the connection."""
        mock_direct_messenger.socket = MagicMock()
        mock_direct_messenger.close()
        mock_direct_messenger.socket.close.assert_called_once()