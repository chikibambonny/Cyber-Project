import logging
from config import *
from queue import SimpleQueue

# =========== LOGGING ===========
LOG_FILE = 'LOG.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=LOG_FORMAT)


def write_to_log(msg):
    logging.info(msg)
    print(msg)


def create_msg(action: str, data: tuple):
    msg = ""
    if action in ACTIONS:
        msg = action + ACT_DELIMITER
        # add all the args
        for arg in data:
            msg += arg + ARG_DELIMITER
        # remove the last char (an excessive delimiter)
        msg = msg[:-1]
        # msg = f"{len(msg):HEADER}{msg}"
        write_to_log(f"[Protocol] - create msg - message created: {msg}")
        return msg
    else:
        write_to_log(f"[Protocol] - create msg - unsupported action: {action}")


def parse_msg(msg: str):
    # split msg to action and data
    split_msg = msg.split(ACT_DELIMITER)
    # get the action
    action = split_msg[0]
    # get the data
    data = tuple(split_msg[1].split(ARG_DELIMITER))
    write_to_log(f"[Protocol] - parse msg - message parsed to action: {action}, data: {data}")
    return action, data


# Message object to encapsulate action and data
class Message:
    def __init__(self, action, data=None):
        self.action = action  # Action type (e.g., authentication, msg, logout)
        self.data = data  # Additional data
        return
