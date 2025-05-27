# ICS 32
# Assignment #1: Diary
#
# Author: Aaron Imani
#
# v0.1.0

# You should review this code to identify what features you need to support
# in your program for assignment 1.
#
# YOU DO NOT NEED TO READ OR UNDERSTAND THE JSON SERIALIZATION ASPECTS OF THIS CODE 
# RIGHT NOW, though can you certainly take a look at it if you are curious since we 
# already covered a bit of the JSON format in class.

import json, time
from pathlib import Path
#from ds_messenger import DirectMessage

class NotebookFileError(Exception):
    """
    NotebookFileError is a custom exception handler that you should catch in your own code. It
    is raised when attempting to load or save Notebook objects to file the system.
    """
    pass

class IncorrectNotebookError(Exception):
    """
    NotebookError is a custom exception handler that you should catch in your own code. It
    is raised when attempting to deserialize a notebook file to a Notebook object.
    """
    pass


class Diary(dict):
    """ 

    The Diary class is responsible for working with individual user diaries. It currently 
    supports two features: A timestamp property that is set upon instantiation and 
    when the entry object is set and an entry property that stores the diary message.

    """
    def __init__(self, entry:str = None, timestamp:float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)

        # Subclass dict to expose Diary properties for serialization
        # Don't worry about this!
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)
    
    def set_entry(self, entry):
        self._entry = entry 
        dict.__setitem__(self, 'entry', entry)

        # If timestamp has not been set, generate a new from time module
        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self):
        return self._entry
    
    def set_time(self, time:float):
        self._timestamp = time
        dict.__setitem__(self, 'timestamp', time)
    
    def get_time(self):
        return self._timestamp

    """

    The property method is used to support get and set capability for entry and 
    time values. When the value for entry is changed, or set, the timestamp field is 
    updated to the current time.

    """ 
    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)

class DirectMessage:
  def __init__(self, recipient=None, message=None, sender=None, timestamp=None):
      self.recipient = recipient
      self.message = message
      self.sender = sender
      self.timestamp = timestamp
    
class Notebook:
    """Notebook is a class that can be used to manage a diary notebook."""

    def __init__(self, username: str, password: str, server:str):
        """Creates a new Notebook object. """
        self.username = username 
        self.password = password 
        self.server = server
        self.contacts = []
        self.messages = [] #a list of direct message objects
        self.file_path = None
    
    def add_message(self, msg) -> None:
        '''
        adds messages with direct message object
        '''
        self.messages.append(msg)

    def add_contact(self, contact):
        """Adds a contact if not already present and not the user themselves."""
        if contact != self.username and contact not in self.contacts:
            self.contacts.append(contact)

    def get_messages(self, contact: str) -> list:
        return self.messages
    
    def get_contacts(self):
        return self.contacts
    
    def set_file_path(self, path):
        self.file_path = Path(path)
    
    def save(self, file_path: str = None) -> None:
        """
        Saves the notebook to a DSU file.
        
        Args:
            file_path: Path to save the notebook. If None, uses self._file_path
        """
        if file_path:
            self.file_path = Path(file_path)
            
        if not self.file_path:
            raise NotebookFileError("No file path specified")
            
        # Prepare data for serialization
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
        except Exception as e:
            raise NotebookFileError(f"Error saving notebook: {e}")

    def load(self, file_path):
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding="utf-8") as file_path:
                    file = json.load(file_path)
                    self.username = file['username']
                    self.password = file['password']
                    self.server = file.get('server', '')
                    self.contacts = file['contacts']
                    self.file_path = path
                
                #change message dictionaries into direct msg objects to load it out
                self.messages = []
                for msg_data in file['messages']:
                    msg = DirectMessage(
                        recipient=msg_data['recipient'],
                        sender=msg_data['sender'],
                        message=msg_data['message'],
                        timestamp=msg_data.get('timestamp', time.time())
                    )
                    self.messages.append(msg)
            except Exception as e:
                raise NotebookFileError(f"Error loading notebook: {e}")

        else:
            print(("Missing required fields in notebook file"))


    def add_diary(self, diary: Diary) -> None:
        """Accepts a Diary object as parameter and appends it to the diary list. Diaries 
        are stored in a list object in the order they are added. So if multiple Diary objects 
        are created, but added to the Profile in a different order, it is possible for the 
        list to not be sorted by the Diary.timestamp property. So take caution as to how you 
        implement your add_diary code.

        """
        self._diaries.append(diary)


    def del_diary(self, index: int) -> bool:
        """
        Removes a Diary at a given index and returns `True` if successful and `False` if an invalid index was supplied. 

        To determine which diary to delete you must implement your own search operation on 
        the diary returned from the get_diaries function to find the correct index.

        """
        try:
            del self._diaries[index]
            return True
        except IndexError:
            return False
        
    def get_diaries(self) -> list[Diary]:
        """Returns the list object containing all diaries that have been added to the Notebook object"""
        return self._diaries