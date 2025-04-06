import logging
import socket
from datetime import datetime
import socket
import random


# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Open the log file in write mode, which truncates the file to zero length
with open(LOG_FILE, 'w'):  # write in log file and delete all that was there before
    pass

SERVER_HOST: str = "0.0.0.0"
CLIENT_HOST: str = "127.0.0.1"
PORT: int = 12345
BUFFER_SIZE: int = 1024
HEADER_LEN: int = 4  # !!!
FORMAT: str = 'utf-8'

DISCONNECT_MSG: str = "EXIT"

# Protocol26 and 27
Cpr26 = ["TIME", "NAME", "RAND", "EXIT", DISCONNECT_MSG]
# Cpr27 = ["DIR", "DELETE", "SEND_PHOTO", "EXECUTE", "TAKE_SCREENSHOT", "COPY", "REG"]


def write_to_log(msg):
    logging.info(msg)
    print(msg)


def check_cmd(data):
    """Check if the command is defined in the protocol (e.g. RAND, NAME, TIME, EXIT)"""
    return data in Cpr26


def create_request_msg(data):
    """Create a valid protocol message, will be sent by client, with length field"""
    request = ''
    if data in ("TIME", "NAME", "RAND", "EXIT"):
        request = "04" + data

    return request


def create_response_msg(data):
    """Create a valid protocol message, will be sent by server, with length field"""
    response = "05Error"
    if data == "TIME":
        response = str(datetime.now())
    elif data == "NAME":
        response = socket.gethostname()[0]
    elif data == "RAND":
        response = f"{random.randint(1, 1000)}"
    elif data == "EXIT":
        response = "Bye"
    return f"{len(response):02}{response}"


def get_msg(my_socket: socket):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """
    str_header = my_socket.recv(2).decode()
    write_to_log(f"[Protocol] str_header - {str_header}")
    length = int(str_header)
    write_to_log(f"[Protocol] length - {length}")
    if length > 0:
        buf = my_socket.recv(length).decode()
    else:
        return False, ""

    return True, buf
