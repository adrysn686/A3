# ds_messenger.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# AUDREY SUN
# AUDRES6@UCI.EDU
# 32241248
import socket
import time
import json
from datetime import datetime
from ds_protocol import extract_json, authentication_json, direct_msg_json, fetch_json

class DirectMessage:
  def __init__(self, message=None, recipient=None, timestamp=None, sender=None):
    self.recipient = recipient   #who you're going to send the msg to
    self.message = message     #message content
    self.sender = sender      #when you receive a message
    self.timestamp = timestamp   #when the message was sent

class DirectMessenger:
  def __init__(self,username=None, password=None):
    self.username = username
    self.password = password
    self.token = None
    self.socket = None
    self.server = None
    self.port = None

  def start_client(self, server, port):
      """Connect to the server"""
      self.server = server
      self.port = port
      try:
          self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.socket.connect((self.server, int(self.port)))
          return self._authenticate()  
      except Exception as e:
          raise ConnectionError(f"Connection failed: {e}")
  
  def _authenticate(self):
      """Authenticate with the server"""
      auth_msg = authentication_json(self.username, self.password)  
      response = self._send_command(auth_msg)
      
      if response and response.type == "ok":
          self.token = response.token
          return True
      else:
          error_msg = response.message if response else "No response from server"
          raise ConnectionError(f"Connection failed: {error_msg}")
  
  def send(self, recipient, message):
      """Send a direct message to another user"""
      if not self.token:
          print("Not authenticated. Please authenticate first.")
          return False
      
      timestamp = str(time.time())
      msg = direct_msg_json(self.token, message, recipient, timestamp)
      response = self._send_command(msg)

      if response and response.type == "ok":
          return True
      else:
          error_msg = response.message if response else "No response from server"
          raise ConnectionError(f"Connection failed: {error_msg}")
  
  def retrieve_new(self):
        """Fetch only unread messages"""
        return self._fetch_messages("unread")

  def retrieve_all(self):
      """Fetch all messages (read and unread)"""
      return self._fetch_messages("all")

  
  def _fetch_messages(self, fetch_type):
      """Internal method to fetch messages"""
      if not self.token:
          raise ConnectionError(f"not authenticated.")
      
      msg = fetch_json(self.token, fetch_type)
      response = self._send_command(msg)

      if response and response.type == "ok":
            messages = []
            for msg_dict in response.messages:
                # Convert server message format to DirectMessage objects
                dm = DirectMessage(
                    message=msg_dict.get('message'),
                    recipient=msg_dict.get('to'),
                    timestamp=msg_dict.get('timestamp'),
                    sender=msg_dict.get('from')
                )
                messages.append(dm)
            return messages
      else:
          error_msg = response.message if response else "No response from server"
          raise ConnectionError(f"Connection failed: {error_msg}")
  
  def _send_command(self, command):
      """Send a command to the server and return the response"""
      try:
          # Send command with proper termination
          self.socket.sendall(json.dumps(command).encode('utf-8') + b'\r\n')
          
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
              return extract_json(data.decode('utf-8').strip())
          return None
      except json.JSONDecodeError as e:
          raise ConnectionError(f"Failed to parse server response: {e}")
      except Exception as e:
          raise ConnectionError(f"Communication error: {e}")

  
  def close(self):
      """Close the connection"""
      if self.socket:
          try:
              self.socket.close()
              print("Connection closed")
          except Exception as e:
              raise ConnectionError(f"Error closing connection: {e}")

