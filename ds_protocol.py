'''This protocol file parses messages and formats into json'''
# ds_protocol.py

# AUDREY SUN
# AUDRES6@UCI.EDU
# 32241248

import json
from collections import namedtuple

# Create a namedtuple to hold the
# values we expect to retrieve from json messages.
# this is the server's response
DSPResponse = namedtuple(
    'DSPResponse', ['type', 'message', 'token', 'messages'])


def extract_json(json_msg: str) -> DSPResponse:
    '''
    Call the json.loads function on a json string
    and convert it to a namedtuple
    '''
    try:
        json_obj = json.loads(json_msg)
        response = json_obj['response']
        message_type = response['type']
        msg = response.get('message', '')
        token = response.get('token')
        messages = response.get('messages', [])
        return DSPResponse(
            type=message_type,
            message=msg, token=token,
            messages=messages
            )

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON error: {e}") from e


def authentication_json(username: str, pwd: str) -> str:
    """Authenticates user"""
    if not username or not pwd:
        raise ValueError("Username and password cannot be empty")
    return json.dumps(
        {"authenticate": {"username": username, "password": pwd}})


def direct_msg_json(tok: str, msg: str, to: str, time: str) -> str:
    """parsing for sending a msg"""
    if not all([tok, msg, to, time]):
        raise ValueError("All fields have to be filled out")
    return json.dumps(
        {"token": tok, "directmessage":
         {"entry": msg, "recipient": to,
          "timestamp": time}})


def fetch_json(token: str, fetch: str) -> str:
    """fetches messages"""
    return json.dumps({"token": token, "fetch": fetch})
