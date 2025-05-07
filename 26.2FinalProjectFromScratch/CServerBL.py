#!/usr/bin/python
import socket
from queue import SimpleQueue
from threading import Thread
from config import *
from protocol import *
import random


# Class to handle client connections
class ClientConnection:
    def __init__(self, connection, address, login: str = ANON_NAME, num: int = 0):
        self.connection = connection  # Client socket
        self.address = address  # Client address
        self.crypto = CryptoProtocol()
        # self.login = login  # Client login name
        self.qin = SimpleQueue()  # Queue for incoming messages
        self.qout = SimpleQueue()  # Queue for outgoing messages
        self.qsuper = None  # Will be set later
        self.ci = None  # Input thread
        self.co = None  # Output thread
        if login == ANON_NAME:
            self.login = login + str(num)
        else:
            self.login = login




# Message object to encapsulate action and data
class Message:
    def __init__(self, action, sender: ClientConnection, data=None):
        self.action = action
        self.sender = sender  # ClientConnection object
        self.data = data  # Additional data (depends on action)


# Server class to manage connections and messages
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected = {}  # {login: (ClientConnection, role)}
        self.count_anon = 0  # Anonymous users unique id
        self.users = ('a', 'b')  # List of allowed users
        self.super_queue = SimpleQueue()  # Main queue for messages
        self.sock = None
        self.current_word: str = ""
        self.guessed: str = ""  # login of the one who guessed

    # receive incoming messages from the client
    def clientin(self, client):
        while True:
            try:
                # msg = client.connection.recv(BUFFER_SIZE).decode()
                encrypted = client.connection.recv(BUFFER_SIZE)
                msg = client.crypto.decrypt(encrypted).decode()

                write_to_log(f'[ServerBL] - clientin - received msg: {msg}')
                if not msg:
                   break
                action, data = parse_msg(msg)
                write_to_log(f'[ServerBL] - clientin - parsed msg: {action}, {str(data)}')
                self.super_queue.put(Message(action, client, data))
            except Exception as e:
                write_to_log(f'[Server] - clientin - exception: {e}')
                break
        # self.super_queue.put(Message(EXIT_ACTION, client))

    # send outcoming messages to the client
    def clientout(self, client):
        client.qout.put(Message(TEXT_ACTION, self.connected['root'], WELCOME_MSG))
        while True:
            m = client.qout.get()
            if m.action == EXIT_ACTION:
                # client.connection.send(b'Good bye\n')
                break
            elif m.data:
                send = create_msg(m.action, m.data)
                #client.connection.send(send.encode())
                encrypted = client.crypto.encrypt(send.encode())
                client.connection.send(encrypted)

    def validate(self, login):
        # if login not in self.users:
          #  return False, 'Permission denied'
        if login in self.connected:
            return False, f'Already logged in from {self.connected[login][0].address}'
        return True, None

    def broadcast(self, client, word):
        word = str(word)  # unpack tuple, in this case the only argument is text which allows to do this by index
        msg = client.login + ': ' + word
        write_to_log(f'[ServerBL] - broadcast - broadcasting : {msg}')
        for connection, role in self.connected.values():
            if connection != client and connection.login != 'root':
                connection.qout.put(Message(TEXT_ACTION, self.connected['root'][0], msg))
        spec_msg = msg = client.login + ' (You): ' + word
        client.qout.put(Message(TEXT_ACTION, self.connected['root'][0], spec_msg))
        write_to_log(f'[ServerBL] - broadcast - broadcasted : {msg}')

    def get_random_word(self):
        with open(WORDS_BANK, "r") as file:
            words = file.read().splitlines()
        return random.choice(words)

    def assign_roles(self) -> str:
        eligible_keys = [k for k in self.connected if k not in ('root', '')]

        if not eligible_keys:
            return ""
        for key in self.connected:
            old_value = self.connected[key]
            self.connected[key] = (old_value[0], GUESS_ROLE)
        if self.guessed == "":
            artist = random.choice(eligible_keys)
            write_to_log(f'[ServerBL] - assign roles- the first artist is {artist}')
        else:
            artist = self.guessed
            write_to_log(f'[ServerBL] - assign roles- the artist is: {artist}, because they guessed: {self.guessed}')
        old_value = self.connected[artist]
        self.connected[artist] = (old_value[0], DRAW_ROLE)
        return artist

    def send_roles(self):
        artist_login = self.assign_roles()
        if artist_login:
            write_to_log(f'[ServerBL] - send roles- artist assigned ')
            for connection, role in self.connected.values():
                if connection.login != 'root':
                    connection.qout.put(Message(ROLE_ACTION, self.connected['root'], str(role)))
            write_to_log(f'[ServerBL] - send roles - roles sent')
            self.broadcast(self.connected['root'][0], f'{artist_login} is drawing now')
            write_to_log(f"[ServerBL] - send roles- broadcasted who's drawing")
            self.current_word = self.get_random_word()
            write_to_log(f'[ServerBL] - send roles- the word is {self.current_word}')
            self.connected[artist_login][0].qout.put(Message(WORD_ACTON, self.connected['root'][0], self.current_word))
            write_to_log(f'[ServerBL] - send roles- the word is sent to the artist')
        else:
            self.broadcast(self.connected['root'][0], 'not enough users to choose roles')


    def run_server(self):
        self.connected['root'] = (ClientConnection(None, None, 'root'), None)
        write_to_log(f'[server] - is running')
        count_anon = 0  # count anonymous users connected

        while True:
            msg = self.super_queue.get()
            write_to_log(f'[Server] - current message: {msg.action} {msg.data}')
            if msg.action == CONNECTION_ACTION:
                connection, address, temp_crypto = msg.data
                write_to_log(f"[Server] - connection action - connection, address  retrieved, current anon_count is {self.count_anon} ")
                client = ClientConnection(connection, address, ANON_NAME, self.count_anon)  # create anonymous connection
                client.crypto = temp_crypto
                write_to_log(f"[Server] - connection action - ClientConnection created for: {client.login}")
                self.connected[client.login] = (client, GUESS_ROLE)  # at the beginning all the players are guessers
                self.count_anon += 1  # increase the count
                write_to_log(f'[ServerBL] - conection action - count_anon updated: {self.count_anon}')
                client.qsuper = self.super_queue
                write_to_log(f"[Server] - connection action - queue started")
                client.ci = Thread(target=self.clientin, args=(client,))
                client.co = Thread(target=self.clientout, args=(client,))
                client.ci.start()
                client.co.start()
                write_to_log(f"[Server] - connection action - threads started")
                client.qout.put(Message(TEXT_ACTION, self.connected['root'], f'You are {client.login}. Login to save progress'))
                # Optionally keep track of unauthenticated clients
            elif msg.action == LOGIN_ACTION:
                client = msg.sender
                write_to_log(f'[Server] DEBUG - current message is from {client.login}')
                username = msg.data[0]
                password = msg.data[1]
                write_to_log(f'[Server] - login action - login: {username}  pass: {password}')
                success, message = authenticate_user(username, password)
                if success:
                    write_to_log(f'[Server] - login - success')
                    is_valid, text_valid = self.validate(username)
                    if is_valid:  # if not connected yet
                        write_to_log(f'[Server] - login - validated')
                        del self.connected[client.login]  # remove the anonymous connection of the same user
                        client.login = username
                        self.connected[username] = (client, GUESS_ROLE)
                        # client.qout.put(Message(TEXT_ACTION, message))
                    else:
                        write_to_log(f'[Server] - login - not validated')
                        # client.qout.put(Message(TEXT_ACTION, message))
                client.qout.put(Message(TEXT_ACTION, self.connected['root'][0], message))

            elif msg.action == SIGNUP_ACTION:
                client = msg.sender
                write_to_log(f'[Server] DEBUG - current message is from {client.login}')
                username = msg.data[0]
                password = msg.data[1]
                write_to_log(f'[Server] - signup action - login: {username}  pass: {password}')
                success, message = register_user(username, password)
                write_to_log(f'[Server] - signup - success: {success}, message: {message}')
                if success:
                    write_to_log(f'[Server] - signup - success')
                    client.login = username
                    self.connected[username] = (client, GUESS_ROLE)
                    # client.qout.put(Message(TEXT_ACTION, message))
                else:
                    write_to_log(f'[Server] - signup - unsuccessful')
                    # client.qout.put(Message(TEXT_ACTION, message))
                client.qout.put(Message(TEXT_ACTION, self.connected['root'][0], message))

            elif msg.action == PLAY_ACTION:
                write_to_log(f'[ServerBL] - play action - play received')
                self.send_roles()

            elif msg.action == TEXT_ACTION:
                client = msg.sender
                write_to_log(f'[Server] DEBUG - current message is from {client.login}')
                write_to_log(f'[ServerBL] - text action - client: {client.login}, data: {msg.data[0]}')
                self.broadcast(client, msg.data[0])
                write_to_log(f'[ServerBL] - text action - BROADCASTED client: {client.login}, data: {msg.data[0]}')
                if self.current_word:
                    write_to_log(f'[ServerBL] - text action - current word exists')
                    print(f"[DEBUG] msg.data: {repr(msg.data)}, curr word: {repr(self.current_word)}")
                    if msg.data[0] == self.current_word:
                        if client.login == self.guessed:
                            client.qout.put(
                                Message(TEXT_ACTION, self.connected['root'][0], "Please keep the word a secret"))
                        else:
                            write_to_log(f'[ServerBL] - received words matches the current word')
                            write_to_log(f'[ServerBL] - text action - the word was guessed: {self.current_word}')
                            self.guessed = client.login
                            self.broadcast(self.connected['root'][0],
                                           f'{self.guessed} guessed the word {self.current_word}')
                            self.send_roles()
                else:
                    write_to_log(f'[ServerBL] - text action - current word doesnt exist')

            elif msg.action == IMAGE_ACTION:
                write_to_log('[ServerBL] - msg action - IMAGE')
                for client, _ in self.connected.values():
                    #if client != msg.sender:
                    client.qout.put(Message(IMAGE_ACTION, self.connected['root'], msg.data))
                    write_to_log('[ServerBL] - msg action - image broadcasted  ')

            elif msg.action == EXIT_ACTION:
                client = msg.sender
                if client:
                    self.broadcast(self.connected['root'][0], f'{client} left')
                    try:
                        del self.connected[client]
                    except KeyError:
                        pass
                client.qout.put(Message(EXIT_ACTION, None))
                client.ci.join()
                client.co.join()
                try:
                    client.connection.shutdown(socket.SHUT_WR)
                    client.connection.close()
                except:
                    pass
            else:
                print('Unknown action')

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        write_to_log(f'[server] - is listening on {self.host}:{self.port}')

        server_thread = Thread(target=self.run_server)
        server_thread.start()

        while True:
            # connection, address = self.sock.accept()
            # self.super_queue.put(Message(CONNECTION_ACTION, self.connected['root'], (connection, address)))
            connection, address = self.sock.accept()

            # Temporary protocol object to handle the key exchange
            temp_crypto = CryptoProtocol()

            # 1. Generate RSA keys and send public key to client
            public_key_pem = temp_crypto.generate_rsa_keys()
            connection.sendall(public_key_pem)

            # 2. Receive encrypted AES key from client
            encrypted_key = connection.recv(512)

            # 3. Decrypt AES key
            temp_crypto.decrypt_symmetric_key(encrypted_key)
            self.super_queue.put(Message(CONNECTION_ACTION, self.connected['root'], (connection, address, temp_crypto)))


# Main function to initialize and run the server
def main():
    server = Server(SERVER_HOST, PORT)
    server.start()


if __name__ == "__main__":
    main()
