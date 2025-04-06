#!/usr/bin/python
import socket
from queue import SimpleQueue
from threading import Thread, current_thread
from config import *
from protocol import *
import random


# Message object to encapsulate action and data
class Message:
    def __init__(self, action, data=None):
        self.action = action  # Action type (e.g., authentication, msg, logout)
        self.data = data  # Additional data


# Class to handle client connections
class ClientConnection:
    def __init__(self, connection, address, file, login):
        self.connection = connection  # Client socket
        self.address = address  # Client address
        self.file = file  # File object for socket communication
        self.login = login  # Client login name
        self.qin = SimpleQueue()  # Queue for incoming messages
        self.qout = SimpleQueue()  # Queue for outgoing messages


# Server class to manage connections and messages
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected = {}  # {login: (ClientConnection, role)}
        self.users = ('a', 'b')  # List of allowed users
        self.super_queue = SimpleQueue()  # Main queue for messages
        self.sock = None
        self.current_word: str = None
        self.guessed: str = None  # login of the one who guessed

    # Handles initial client login
    def gateman(self, connection, address):
        file = connection.makefile(mode='rw', buffering=1)  # Create file object for socket
        file.write('login: ')  # Prompt for login
        file.flush()
        login = file.readline().rstrip()  # Read client input
        write_to_log(f'[CServerBL] - gateman - login: {login}')
        # kostyl
        # act, login = parse_msg(file.readline().rstrip())
        # write_to_log(f'[CServerBL] - gateman - act : {act}, login: {login}')
        # self.super_queue.put(Message(AUTHENTICATION_ACTION, [connection, address, file, login, current_thread()]))

    # Reads incoming messages from client and puts them into the server's queue
    def clientin(self, client):
        for word in client.file:
            client.qsuper.put(Message(TEXT_ACTION, (client, word.rstrip())))  # Put messages into server queue
        client.qsuper.put(Message(LOGOUT_ACTION, client))  # Notify server of client logout

    # Sends outgoing messages to client
    def clientout(self, client):
        client.file.write(f'Welcome\n')  # Welcome message
        client.file.flush()

        while True:
            m = client.qout.get()  # Get message from queue
            if m.action == EXIT_ACTION:  # Exit command
                client.file.write('Good bye\n')
                break
            elif m.action == TEXT_ACTION:  # Regular message
                client.file.write(m.data + '\n')
                client.file.flush()

    # Validates client credentials
    def validate(self, connection, address, file, login):
        if login not in self.users:
            return False, 'Permission denied'  # Reject if login not in users
        if login in self.connected:
            return False, f'Already logged in from {self.connected[login][0].address}'  # Reject if user already connected
        return True, ClientConnection(connection, address, file, login)  # Accept login

    # Broadcasts message to all connected clients (except sender and root)
    def broadcast(self, client, word):
        msg = client.login + ': ' + word
        for connection, role in self.connected.values():  # unpack the tuple
            if not (connection is client or connection.login == 'root'):
                connection.qout.put(Message(TEXT_ACTION, msg))  # Add message to client's outgoing queue

    def get_random_word(self):
        # Open the file and read the words.txt into a list
        with open(WORDS_BANK, "r") as file:
            words = file.read().splitlines()
        # Return a random word from the list
        return random.choice(words)

    def assign_roles(self) -> str:
        if not self.connected:
            msg = 'no clients to assign roles to'
        else:
            for key in self.connected:
                self.connected[key][1] = GUESS_ROLE
            if self.guessed is None:
                artist = random.choice(self.connected.keys())
            else:
                artist = self.guessed
            self.connected[self.artist][1] = DRAW_ROLE
            return artist

    def send_roles(self):
        artist_login = self.assign_roles()
        for connection, role in self.connected.values():
            if not (connection.login == 'root'):
                connection.qout.put(Message(ROLE_ACTION, role))
        self.broadcast(f'[Server] {artist_login} is drawing now')
        self.current_word = self.get_random_word()
        self.connected[artist_login][0].qout.put(Message(WORD_ACTON, self.current_word))


    # Main server function
    def run_server(self):
        self.connected['root'] = (ClientConnection(None, None, None, 'root'), None)  # Root user placeholder
        write_to_log(f'[server] - is running')

        while True:
            msg = self.super_queue.get()  # Get message from queue
            write_to_log(f'[Server] - current message: {msg.data} ')
            # connection, address, file, _ = msg.data
            # write_to_log(f'[CServerBL] - msg.data parse - connection: {connection}, adress: {address}, file: {file}')
            if msg.action == CONNECTION_ACTION:
                g = Thread(target=self.gateman, args=(*msg.data,))  # Start login thread
                g.start()
            elif msg.action == AUTHENTICATION_ACTION:
                gate_thread = msg.data.pop()
                gate_thread.join()  # Wait for login thread to complete
                allow, args = self.validate(*msg.data)  # Validate login
                if allow:
                    # Notify clients of connection
                    self.broadcast(self.connected['root'][0], f'{args.login} connected from {args.address}')
                    args.qsuper = self.super_queue
                    # Start input thread
                    args.ci = Thread(target=self.clientin, args=(args,))
                    # Start output thread
                    args.co = Thread(target=self.clientout, args=(args,))
                    args.ci.start()
                    args.co.start()
                    self.connected[args.login] = (args, GUESS_ROLE)  # Add client to connected list
                else:
                    connection, address, file, _ = msg.data
                    file.write(args + '\n')  # Send error message to client
                    file.flush()
                    file.close()
                    connection.shutdown(socket.SHUT_WR)
                    connection.close()
            elif msg.action == PLAY_ACTION:
                # Send roles and the word
                self.send_roles()
            elif msg.action == TEXT_ACTION:
                self.broadcast(*msg.data)  # Broadcast message
                if self.current_word:
                    connection, address, file, _ = msg.data
                    write_to_log(f'[CServerBL] - msg.data parse - connection: {connection}, adress: {address}, file: {file}')
                    if file == self.current_word:
                        self.guessed = connection.login
                        self.broadcast(f'{self.guessed} guessed the word {self.current_word}')
                        self.send_roles()

            elif msg.action == EXIT_ACTION:
                self.broadcast(self.connected['root'][0], f'{msg.data.login} left')  # Notify clients of logout
                msg.data.qout.put(Message('exit'))  # Send exit message
                msg.data.ci.join()
                msg.data.co.join()
                try:
                    msg.data.file.close()
                    msg.data.connection.shutdown(socket.SHUT_WR)
                    msg.data.connection.close()
                except:
                    pass
                del self.connected[msg.data.login]  # Remove client from connected list
            else:
                print('Unknown action')  # Debug unknown actions


    # Start the server
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket
        self.sock.bind((self.host, self.port))  # Bind socket to host and port
        self.sock.listen()  # Start listening for connections
        write_to_log(f'[server] - is listening on {self.host}:{self.port}')

        # Start the server thread
        server_thread = Thread(target=self.run_server)
        server_thread.start()

        # Accept client connections and add them to the queue
        while True:
            self.super_queue.put(Message(CONNECTION_ACTION, self.sock.accept()))


# Main function to initialize and run the server
def main():
    server = Server(SERVER_HOST, PORT)
    server.start()


if __name__ == "__main__":
    main()
