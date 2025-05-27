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
  def __init__(self, dsuserver='127.0.0.1', username=None, password=None):
      self.host = dsuserver
      self.port = 3001
      self.token = None
      self.username = username
      self.password = password
      self.socket = None
    
  def connect(self):
    """Connect to the server"""
    try:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
  def _authenticate(self):
    """Authenticate with the server using stored credentials"""
    if not self.username or not self.password:
        return False
        
    # Use ds_protocol's authentication_json to format the request
    auth_msg = authentication_json(self.username, self.password)
    response = self._send_command(auth_msg)
    
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

    #save locally first
    self
    if not self.token and not self._authenticate():
        print("Not authenticated. Please authenticate first.")
        return False
        
    # Use ds_protocol's direct_msg_json to format the message
    timestamp = str(datetime.now().timestamp())
    msg_json = direct_msg_json(self.token, message, recipient, timestamp)
    response = self._send_command(msg_json)
    
    if response:
        dsp_response = extract_json(response)
        if dsp_response.type == "ok":
            print(f"Message sent to {recipient}")
            return True
        else:
            print(f"Failed to send message: {dsp_response.message}")
    else:
        print("No response from server when sending message")
    return False
    
  def retrieve_all(self) -> list:
    """Retrieve all messages (read and unread)"""
    return self._retrieve_messages("all")
    
  def retrieve_new(self) -> list:
    """Retrieve only unread messages"""
    return self._retrieve_messages("unread")
    
  def _retrieve_messages(self, fetch_type) -> list:
    """Internal method to retrieve messages"""
    if not self.token and not self._authenticate():
        print("Not authenticated. Please authenticate first.")
        return []
        
    # Use ds_protocol's fetch_json to format the request
    fetch_msg = fetch_json(self.token, fetch_type)
    response = self._send_command(fetch_msg)
    
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
  
  def _send_command(self, json_msg: str):
    """Send a JSON command to the server and return the response"""
    try:
        if not self.socket or not self._is_connected():
            self.connect()
            
        # Send command with proper termination
        self.socket.sendall(json_msg.encode('utf-8') + b'\r\n')
        
        # Receive response
        data = b''
        while True:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
            data += chunk
            if b'\r\n' in chunk:  # Look for message terminator
                break
        
        if data:
            return data.decode('utf-8').strip()
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse server response: {e}")
        return None
    except Exception as e:
        print(f"Communication error: {e}")
        return None
            
  def _is_connected(self):
    """Check if socket is still connected"""
    try:
        # Try to get socket status
        self.socket.getpeername()
        return True
    except:
        return False
  
  def close(self):
    """Close the connection"""
    if self.socket:
        try:
            self.socket.close()
            print("Connection closed")
        except Exception as e:
            print(f"Error closing connection: {e}")