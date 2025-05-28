import pytest
import json
import socket
from unittest.mock import MagicMock, patch
from ds_messenger import DirectMessenger, DirectMessage

@pytest.fixture
def messenger():
    """creates an object of DirectMessenger"""
    messenger_obj = DirectMessenger(dsuserver='127.0.0.1', username='bob', password = '123')
    messenger_obj.socket = MagicMock()
    return messenger_obj

def test_connection_works(messenger_obj):
    """tests if connection works properly"""
    with patch('socket.socket') as mock_socket:
        mock_socket_obj = MagicMock()
        mock_socket.return_value = mock_socket_obj


