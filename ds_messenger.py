# ds_messenger.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# AUDREY SUN
# AUDRES6@UCI.EDU
# 32241248
import socket
import time
import json
from ds_protocol import extract_json, authentication_json, direct_msg_json, fetch_json

class DirectMessage:
  def __init__(self):
    self.recipient = None   #who you're going to send the msg to
    self.message = None     #message content
    self.sender = None      #when you receive a message
    self.timestamp = None   #when the message was sent

class DirectMessenger:
  def __init__(self, dsuserver=None, username=None, password=None):
    self.token = None
    self.dsuserver = dsuserver
    self.username = username
    self.password = password
    self.send_file = None
    self.recv_file = None
    self.client = None
	# more code should go in here

  def start_client(self, server_address, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
      client.connect((server_address, int(server_port)))

      self.send_file = client.makefile("w")
      self.recv_file = client.makefile("r")

      authentication_msg = authentication_json(self.username, self.password)
      self.send_file.write(authentication_msg + '\r\n')
      self.send_file.flush()

      resp = self.recv_file.readline()
      resp_list = resp.split()
      token_unparsed = resp_list[-1]
      self.token = token_unparsed[1:-3]
      #print(self.token)
      #print(resp)
      
    	
  def send(self, message:str, recipient:str) -> bool:
    # must return true if message successfully sent, false if send failed.
    try:
      msg = direct_msg_json(self.token, message, recipient, time.time())
      self.send_file.write(msg + '\r\n')
      self.send_file.flush()
      return True 
    except:
      return False
		
  def retrieve_new(self) -> list:
    # must return a list of DirectMessage objects containing all new messages
    msg = fetch_json(self.token, "unread")
    self.send_file.write(msg + '\r\n')
    self.send_file.flush()
    resp = self.recv_file.readline() 
    #resp = self.recv_file.readline()
    print(resp)
    parsed_json = extract_json(resp)
    
    message_lst = []
    #parsed_json.messages is a list of message data dictionaries 

    for msg_data in parsed_json.messages:
      direct_msg = DirectMessage()
      direct_msg.message = msg_data.get('message', '')
      direct_msg.timestamp = msg_data.get('timestamp', 0)

      if "recipient" in msg_data:
        direct_msg.recipient = msg_data.get('recipient', '')
      else:
        direct_msg.sender = msg_data['from']

      message_lst.append(direct_msg)
    
    return message_lst
  
  def retrieve_all(self) -> list:
    # must return a list of DirectMessage objects containing all messages
    msg = fetch_json(self.token, "all")
    self.send_file.write(msg + '\r\n')
    self.send_file.flush()
    
    #resp = self.recv_file.readline()
    #self.client.settimeout(5)
    try:
      resp = self.recv_file.readline()
    except Exception as e:
        print("Error in retrieve_all:", e)
    
    parsed_json = extract_json(resp)
    
    message_lst = []
    #parsed_json.messages is a list of message data dictionaries 

    for msg_data in parsed_json.get('messages', []):
      direct_msg = DirectMessage()
      direct_msg.message = msg_data.get('message', '')
      direct_msg.timestamp = msg_data.get('timestamp', 0)

      if "recipient" in msg_data:
        direct_msg.recipient = msg_data.get('recipient', '')
      else:
        direct_msg.sender = msg_data['from']

      message_lst.append(direct_msg)
    
    return message_lst


  
  def get_msg(self):
    return extract_json(self.recv_file.readline())

  def _send(self, message:str):
    self.send_file.write(message + '\n')
    self.send_file.flush()

  def _retrieve_messages(self, fetch: str) -> list:
    msg = fetch_json(self.token, fetch)
    self._send(msg)