from CProtocol import *
from datetime import datetime
import socket
import random


class CProtocol26():
    def __init__(self):
        super().__init__()

    def create_request_msg(self, data) -> str:
        """Create a valid protocol message, will be sent by client, with length field
        """
        # we add before msg itself its length, so we can tell how much space the message is going to take
        request = ""
        if data == "TIME" or data == "NAME" or data == "RAND" or data == "EXIT":
            request = "0004" + data  # all our commands are 4 bits, but it weren't like this we would
            # do length and convert it to binary
        write_to_log("[CPROTOCOL26 - CRT-MSG] request - " + request)
        return request

    def create_response_msg(self, data) -> str:
        # creates response msg according to what command user sent
        """Create a valid protocol message, will be sent by server, with length field"""
        response = "05Error"
        write_to_log("[CPROTOCOL26] creates response msg with -" + data)
        if data == "TIME":
            response = str(datetime.now())
        elif data == "NAME":
            response = socket.gethostname()

        elif data == "RAND":
            response = f"{random.randint(1, 1000)}"
        elif data == DISCONNECT_MSG:
            response = DISCONNECT_MSG

        return f"{len(response):04d}{response}"  # add two bits of response length in the beginning
