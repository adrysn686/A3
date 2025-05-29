'''this module saves notebooks locally'''
import json
import time
from pathlib import Path


class DirectMessage:
    '''This DirectMessage class formats a message object'''
    def __init__(
            self, recipient=None, message=None, sender=None, timestamp=None
    ) -> None:
        self.recipient = recipient
        self.message = message
        self.sender = sender
        self.timestamp = timestamp

    def get_recipient(self):
        '''use to get recipient'''
        return self.recipient

    def get_message(self):
        '''use to get message'''
        return self.message


class Notebook:
    """Notebook is a class that can be used to manage a diary notebook."""

    def __init__(self, username: str, password: str, server: str):
        """Creates a new Notebook object. """
        self.username = username
        self.password = password
        self.server = server
        self.contacts = []
        self.messages = []  # a list of direct message objects
        self.file_path = None

    def add_message(self, msg) -> None:
        '''
        adds messages with direct message object
        '''
        self.messages.append(msg)

    def add_contact(self, contact):
        """Adds a contact"""
        if (
            contact != self.username and
            contact not in self.contacts and
            isinstance(contact, str)
        ):
            self.contacts.append(contact)

    def get_messages(self, contact: str) -> list:
        '''method gets messages'''
        if contact is not None:
            return self.messages
        return None

    def get_contacts(self):
        '''method gets contacts'''
        return self.contacts

    def set_file_path(self, path):
        '''this sets file path'''
        self.file_path = Path(path)

    def save(self, file_path: str = None) -> None:
        """
        Saves the notebook to a JSON file.
        Args:
            file_path: Path to save the notebook. If None, uses self._file_path
        """
        if file_path:
            self.file_path = Path(file_path)

        if not self.file_path:
            raise ValueError("No file path specified")

        data = {
            'username': self.username,
            'password': self.password,
            'server': self.server,
            'contacts': self.contacts,
            'messages': [{
                'recipient': msg.recipient,
                'sender': msg.sender,
                'message': msg.message,
                'timestamp': msg.timestamp
            } for msg in self.messages]
        }

        try:
            # Create parent directory if it doesn't exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"Error saving notebook: {e}")

    def load(self, file_path):
        '''loads notebook'''
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding="utf-8") as f:
                    file = json.load(f)
                    self.username = file['username']
                    self.password = file['password']
                    self.server = file.get('server', '')
                    self.contacts = file['contacts']
                    self.file_path = path

                self.messages = []
                for msg_data in file['messages']:
                    msg = DirectMessage(
                        recipient=msg_data['recipient'],
                        sender=msg_data['sender'],
                        message=msg_data['message'],
                        timestamp=msg_data.get('timestamp', time.time())
                    )
                    self.messages.append(msg)
            except json.JSONDecodeError:
                print("Invalid JSON format")
            except OSError:
                print("Could not load notebook file.")

        else:
            print(("Missing required fields in notebook file"))
