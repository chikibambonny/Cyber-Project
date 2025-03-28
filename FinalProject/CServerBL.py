import json
import socket
import threading
import random
from CProtocol import *


# events
NEW_CONNECTION: int = 1
CLOSE_CONNECTION: int = 2
NEW_REGISTRATION: int = 3


class CServerBL:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._server_socket = None
        self._is_srv_running = True
        self._accepting_connections = True  # Flag to control connection acceptance
        self._client_handlers = {}  # dictionary of connected clients and their roles
        self._register_clients = []
        self._stop_message = "STOP_CONNECTIONS"  # Special message to stop accepting connections

    def stop_accepting_connections(self):
        """Stop the server from accepting new connections."""
        self._accepting_connections = False
        write_to_log("[CServerBL] Server stopped accepting new connections.")

    def select_random_client(self):
        """Select a random connected client."""
        if not self._client_handlers:
            write_to_log("[CServerBL] No clients to select from.")
            return None
        selected_client = random.choice(self._client_handlers.keys())
        write_to_log(f"[CServerBL] Selected random client: {selected_client}. They're drawing now")
        return selected_client

    def send_roles(self, chosen_client):
        for client in self._client_handlers:
            # create role setting message
            msg = create_message(COMMAND_ROLE, self._client_handlers[client])
            client.send(msg.encode())
            write_to_log(f"[CServerBL] sent role {self._client_handlers[client]} to {client} ")

    def assign_roles(self, guessed: socket = None):
        if not self._client_handlers:
            write_to_log("[CServerBL] No clients to select from.")
        # setting everyone's roles to default
        for key in self._client_handlers:
            self._client_handlers[key] = DEFROLE
        # assigning the drawing role
        # if noone has guessed (first play)
        if guessed is None:
            chosen_client = random.choice(self._client_handlers.keys())
            write_to_log(f"[CServerBL] Chosen random client: {chosen_client}")
        else:
            self._client_handlers[guessed] = ARTROLE
        # send roles
        self.send_roles(guessed)

    def start_server(self):
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen(5)
            write_to_log(f"[SERVER_BL] Server is listening on {self._host}:{self._port}")
            self._is_srv_running = True
            self._accepting_connections = True

            while self._is_srv_running:

                while self._accepting_connections:
                    client_socket, address = self._server_socket.accept()
                    write_to_log(f"[SERVER_BL] Client connected: {address}")
                    cl_handler = CClientHandler(client_socket, address, self.handle_message)
                    cl_handler.start()
                    self._client_handlers[cl_handler] = DEFROLE  # add new connection + assign default role
                    write_to_log(f"[SERVER_BL] Active connections: {len(self._client_handlers)}")

                    if parse_message(self._client_socket) == COMMAND_PLAY:
                        self._accepting_connections = False
                        write_to_log(f"[SERVER_BL] The game is starting, the server doesn't receive connections anymore")
                # here starts the game
                while True:
                    # assign roles
                    assign_roles()
                    # chose a random word and send it
                    current_word = get_random_word()
                    # accept guesses while not guessed (while true)
                    while True:
                        # treat guesses

                        # if right
                        # stop accessing guesses
                    # notificate everybody
                    # update "guessed"
                    # update scores
                    # break






























                if not self._accepting_connections:
                    write_to_log("[SERVER_BL] Stopped accepting connections.")
                    break

                client_socket, address = self._server_socket.accept()
                write_to_log(f"[SERVER_BL] Client connected: {address}")
                cl_handler = CClientHandler(client_socket, address, self.handle_message)
                cl_handler.start()
                self._client_handlers.append(cl_handler)
                write_to_log(f"[SERVER_BL] Active connections: {len(self._client_handlers)}")

        except Exception as e:
            write_to_log(f"[SERVER_BL] Exception in start_server: {e}")

        finally:
            write_to_log("[SERVER_BL] Server thread terminated.")






    def handle_message(self, message, client_handler):
        """Handle incoming messages from clients."""
        if message == self._stop_message:
            write_to_log("[SERVER_BL] Received stop message.")
            self.stop_accepting_connections()


class CClientHandler(threading.Thread):
    def __init__(self, client_socket, address, message_handler):
        super().__init__()
        self._client_socket = client_socket
        self._address = address
        self.message_handler = message_handler
        self.connected = True

    def send_message(self, message):
        self._client_socket.send(message.encode(FORMAT))

    def run(self):
        while self.connected:
            valid_msg, message = receive_msg(self._client_socket)
            if valid_msg:
                write_to_log(f"[CLIENT_HANDLER] Message from {self._address}: {message}")
                self.message_handler(message, self)

            # Handle DISCONNECT
            if message == DISCONNECT_MSG:
                self.connected = False
                write_to_log(f"[CLIENT_HANDLER] Client {self._address} disconnected.")
                self._client_socket.close()
