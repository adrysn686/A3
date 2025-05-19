# ds_protocol.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# AUDREY SUN 
# AUDRES6@UCI.EDU
# 32241248

import time
import json
from collections import namedtuple

# Create a namedtuple to hold the values we expect to retrieve from json messages.
# this is the server's response
DSPResponse = namedtuple('DSPResponse', ['type','message', 'token', 'messages'])

def extract_json(json_msg:str) -> DSPResponse:
  '''
  Call the json.loads function on a json string and convert it to a DataTuple object
  '''
  try:
    json_obj = json.loads(json_msg)
    response = json_obj['response']
    message_type = response['type']
    msg = response.get('message', '')
    token = response.get('token')
    messages = response.get('messages', [])


  except json.JSONDecodeError:
    print("Json cannot be decoded.")

  return DSPResponse(type=message_type, message=msg, token = token, messages = messages)

def authentication_json(username, pwd):
  return json.dumps({"authenticate": {"username": username, "password": pwd}})

def direct_msg_json(token, entry, recipient, timestamp):

  return json.dumps({"token": token, "directmessage": {"entry": entry, "recipient": recipient, "timestamp": timestamp}})

def fetch_json(token, fetch):
  return json.dumps({"token": token, "fetch": fetch})

