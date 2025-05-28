# ds_messenger.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# AUDREY SUN
# AUDRES6@UCI.EDU
# 32241248
import socket
import json
import time
from notebook import Notebook
from datetime import datetime
from ds_protocol import extract_json, authentication_json, direct_msg_json, fetch_json

class DirectMessage:
    def __init__(self, recipient=None, message=None, sender=None, timestamp=None):
        self.recipient = recipient
        self.message = message
        self.sender = sender
        self.timestamp = timestamp

class DirectMessenger:
    def __init__(self, dsuserver=None, username=None, password=None):
        self.host = dsuserver
        self.port = 3001
        self.token = None
        self.username = username
        self.password = password
        self.socket = None
        
        if dsuserver and username and password:
            self.__connect()
            self.__authenticate()
    
    def __connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            return True
        except socket.timeout:
            print("Connection timed out")
            return False
    
    def __authenticate(self):
        """Authenticate with the server using stored credentials"""
        if not self.username or not self.password:
            return False
            
        # Use ds_protocol's authentication_json to format the request
        auth_msg = authentication_json(self.username, self.password)
        response = self.__send_command(auth_msg)
        
        if response:
            dsp_response = extract_json(response)
            if dsp_response.type == "ok":
                self.token = dsp_response.token
                print(f"Authenticated as {self.username}")
                return True
            else:
                print(f"Authentication failed: {dsp_response.message}")
        else:
            print("No response from server during authentication")
        return False

    def send(self, message: str, recipient: str) -> bool:
        """Send a direct message to another user"""

        if not self.token and not self.__authenticate():
            print("Not authenticated. Please authenticate first.")
            return False
            
        # Use ds_protocol's direct_msg_json to format the message
        timestamp = str(datetime.now().timestamp())
        msg_json = direct_msg_json(self.token, message, recipient, timestamp)
        response = self.__send_command(msg_json)
        
        if response:
            dsp_response = extract_json(response)
            if dsp_response.type == "ok":
                print(f"Message sent to {recipient}")
                return True
            else:
                print(f"Failed to send message: {dsp_response.message}")
                return False
        else:
            print("No response from server when sending message")
        return False
    
    def retrieve_all(self) -> list:
        """Retrieve all messages (read and unread)"""
        return self.__retrieve_messages("all")
        
    def retrieve_new(self) -> list:
        """Retrieve only unread messages"""
        return self.__retrieve_messages("unread")
        
    def __retrieve_messages(self, fetch_type) -> list:
        """Internal method to retrieve messages"""
        if not self.token and not self.__authenticate():
            print("Not authenticated. Please authenticate first.")
            return []
        # Use ds_protocol's fetch_json to format the request
        fetch_msg = fetch_json(self.token, fetch_type)
        response = self.__send_command(fetch_msg)    
        if response:
            dsp_response = extract_json(response)
            if dsp_response.type == "ok":
                messages = []
                for msg in dsp_response.messages:
                    dm = DirectMessage()
                    dm.recipient = msg.get("recipient")
                    dm.message = msg.get("message")
                    dm.sender = msg.get("from")
                    dm.timestamp = msg.get("timestamp")
                    messages.append(dm)
                return messages
            else:
                print(f"Failed to retrieve messages: {dsp_response.message}")
        else:
            print("No response from server when fetching messages")
        return []
 
    def __send_command(self, json_msg: str):
        """Send a JSON command and return the text response"""
        try:
            if not self.socket:
                self.__connect()

            with self.socket.makefile('rw', encoding='utf-8') as client_file:
                client_file.write(json_msg + '\r\n')
                client_file.flush()

                response = client_file.readline()
                return response.strip()

        except ConnectionError as e:
            print(f"Error: {e}")
            return None
        except socket.timeout:
            print("timeout error")
            return None