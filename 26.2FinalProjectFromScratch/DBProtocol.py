from Protocol import *
from config import *
import sqlite3
from argon2 import PasswordHasher, exceptions as argon2_exceptions

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
            return True, f'Logged in as {username}'
        else:
            write_to_log(f'[Protocol] - authenticate - false, incorrect password')
            return False, "Incorrect password."


if __name__ == "__main__":
    init_user_db()