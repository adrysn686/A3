'''This file containts pytest cases for protocol'''
import json
from unittest import TestCase
from ds_protocol import DSPResponse, extract_json, authentication_json, direct_msg_json, fetch_json


class TestProtocol(TestCase):
    '''This class is for formatting/parsing json'''
    def test_extract_json_working(self):
        '''Tests for extract json that works properly'''
        json_msg = json.dumps({
        "response": {
            "type": "ok",
            "message": "working!",
            "token": "123",
            "messages": ["hello", "goodbye"]
        }
    })
        result = DSPResponse(
            type="ok", message="working!", token="123",
            messages=["hello", "goodbye"]
            )
        self.assertEqual(extract_json(json_msg), result)

    def test_extract_json_missing(self):
        '''test for when extract json has missing fields '''
        json_msg = json.dumps({
        "response": {
            "type": "ok",
            "token": None,
        }
    })
        result = DSPResponse(type="ok", message="", token=None, messages=[])
        self.assertEqual(extract_json(json_msg), result)

    def test_extract_json_invalid(self):
        '''test for when extract json is not valid '''
        json_msg = '{this should not work}'
        with self.assertRaises(ValueError):
            extract_json(json_msg)

    def test_authentication_json_working(self):
        '''test for working authentication'''
        username = 'Josh'
        pwd = '123'
        result = json.dumps({"authenticate": {"username": username, "password": pwd}})
        self.assertEqual(authentication_json('Josh', '123'), result)

    def test_authentication_json_no_inputs(self):
        '''test for authentication with no inputs'''
        username = ''
        pwd = ''
        with self.assertRaises(ValueError):
            authentication_json(username, pwd)

    def test_direct_msg_json_working(self):
        '''this tests when direct msg is working'''
        token = "token_example"
        entry = "hello there"
        recipient = "Bob"
        timestamp = "12:04"
        result = json.dumps(
            {"token": token, "directmessage": 
             {"entry": entry, "recipient": recipient, "timestamp": timestamp}
             })
        self.assertEqual(direct_msg_json("token_example", "hello there", "Bob", "12:04"), result)

    def test_direct_msg_json_invalid(self):
        """when fields are missing"""
        token = ""
        entry = ""
        recipient = ""
        timestamp = "12:04"
        with self.assertRaises(ValueError):
            direct_msg_json(token, entry, recipient, timestamp)

    def test_direct_msg_json_invalid_timestamp(self):
        """Test timestamp with a non-string value"""
        token = ""
        entry = ""
        recipient = ""
        timestamp = 12
        with self.assertRaises(ValueError):
            direct_msg_json(token, entry, recipient, timestamp)

    def test_fetch_json(self):
        """test fetch json"""
        token = "token_example"
        fetch = "all"
        result = json.dumps({"token": token, "fetch": fetch})
        self.assertEqual(fetch_json(token, fetch), result)
