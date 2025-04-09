import logging
from config import *
from queue import SimpleQueue
import sqlite3
from argon2 import PasswordHasher, exceptions as argon2_exceptions

# =========== LOGGING ===========
LOG_FILE = 'LOG.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=LOG_FORMAT)


def write_to_log(msg):
    logging.info(msg)
    print(msg)


def create_msg(action: str, data=""):
    msg = ""
    if action in ACTIONS:
        # msg = action + ACT_DELIMITER
        # add all the args
        # for arg in data:
        # msg += arg + ARG_DELIMITER
        # remove the last char (an excessive delimiter)
        # msg = msg[:-1]
        # msg = f"{len(msg):HEADER}{msg}"
        if isinstance(data, tuple):
            msg = action + ACT_DELIMITER
            # add all the args
            for arg in data:
                msg += arg + ARG_DELIMITER
        elif isinstance(data, str):
            msg = action + ACT_DELIMITER + data
            # remove the last char (an excessive delimiter)
        msg = msg[:-1]
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


# =========== DATABASE ===========
def init_user_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    hashed = ph.hash(password)
    write_to_log(f'[Protocol] - hash password - password: {password} , hashed: {hashed}')
    return hashed


def verify_password(hashed_password: str, input_password: str) -> bool:
    """Verify a password against the stored hash."""
    try:
        verify = ph.verify(hashed_password, input_password)
        write_to_log(f'[Protocol] - verify password - result: {verify}')
        return verify
    except argon2_exceptions.VerifyMismatchError as e:
        write_to_log(f'[Protocol] - verify password exception: {e}')
        return False


def register_user(username: str, password: str) -> tuple[bool, str]:
    hashed = hash_password(password)
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
            conn.commit()
            write_to_log(f'[Protocol] - register - user added successfully')
            return True, "Signup successful"
    except Exception as e:
        if e == sqlite3.IntegrityError:
            write_to_log(f'[Protocol] - register - exception - user already exists')
            return False, "Username already exists"
        else:
            write_to_log(f'[Protocol] - register - exception {e} ')
            return False, f"Something went wrong"


def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            write_to_log(f'[Protocol] - authenticate - false, username not found')
            return False, "Username not found."
        elif verify_password(result[0], password):
            write_to_log(f'[Protocol] - authenticate - successful')
            return True, "Login successful."
        else:
            write_to_log(f'[Protocol] - authenticate - false, incorrect password')
            return False, "Incorrect password."






if __name__ == "__main__":
    init_user_db()

