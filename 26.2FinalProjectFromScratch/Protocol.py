import logging
from config import *
from queue import SimpleQueue
import sqlite3
from argon2 import PasswordHasher, exceptions as argon2_exceptions

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


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
            # remove the last char (an excessive delimiter)
            msg = msg[:-1]
        elif isinstance(data, str):
            msg = action + ACT_DELIMITER + data
        elif isinstance(data, bool):
            msg = action + ACT_DELIMITER + str(data)
        else:
            msg = action   # + ACT_DELIMITER + data  # empty string after the delimiter for the PLAY comand
        write_to_log(f"[Protocol] - create msg - message created: {msg}")
        return msg+"\n"
    else:
        write_to_log(f"[Protocol] - create msg - unsupported action: {action}")


def parse_msg(msg: str):
    # split msg to action and data
    msg = msg.replace("\n", "")
    split_msg = msg.split(ACT_DELIMITER)
    # get the action
    action = split_msg[0]
    # get the data
    data = tuple(split_msg[1].split(ARG_DELIMITER))
    write_to_log(f"[Protocol] - parse msg - message parsed to action: {action}, data: {data}")
    return action, data


# =========== ENCRYPTION ===========
class CryptoProtocol:
    def __init__(self):
        # These will be populated depending on the role (client/server)
        self.symmetric_key = None
        self.private_key = None
        self.public_key = None

    # ----- SERVER-SIDE: Generate RSA public/private key pair -----
    def generate_rsa_keys(self):
        # Create a new RSA private key
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        # Extract public key from the private key
        self.public_key = self.private_key.public_key()
        # Return public key as PEM (so it can be sent to client)
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    # (Optional) Load a private key from PEM if stored/needed
    def load_private_key(self, pem_data):
        self.private_key = serialization.load_pem_private_key(pem_data, password=None)

    # ----- CLIENT-SIDE: Create symmetric key and encrypt it with server's public key -----
    def encrypt_symmetric_key(self, server_public_pem):
        # Load the server's public RSA key
        server_public_key = serialization.load_pem_public_key(server_public_pem)
        # Generate a new AES key (256-bit)
        self.symmetric_key = os.urandom(32)
        # Encrypt the AES key using RSA (asymmetric encryption)
        return server_public_key.encrypt(
            self.symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    # ----- SERVER-SIDE: Decrypt AES key using server's private RSA key -----
    def decrypt_symmetric_key(self, encrypted_key):
        # Decrypt the AES key sent by the client
        self.symmetric_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    # ----- Use AES to encrypt any plaintext message (client or server) -----
    def encrypt(self, plaintext: bytes) -> bytes:
        # Generate a random 16-byte IV (initialization vector)
        iv = os.urandom(16)
        # Create AES cipher in CFB mode (good for stream-like data)
        cipher = Cipher(algorithms.AES(self.symmetric_key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        # Encrypt the plaintext
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        # Prepend IV to ciphertext so the recipient can decrypt
        return iv + ciphertext

    # ----- Use AES to decrypt received message (client or server) -----
    def decrypt(self, encrypted_data: bytes) -> bytes:
        # Extract the IV from the first 16 bytes
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        # Create AES cipher with same IV
        cipher = Cipher(algorithms.AES(self.symmetric_key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        # Decrypt and return the plaintext
        return decryptor.update(ciphertext) + decryptor.finalize()





