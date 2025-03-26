import socket
from threading import Thread, Lock
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5 import QtCore
from config import *
from protocol import *


class CClientBL(QObject):
    message_received = pyqtSignal(str)  # Define a signal for received messages
    def __init__(self):
        super().__init__()  # Ensure QObject is initialized
        # self._host = SERVER_HOST
        # self._port = PORT
        self._client_socket = None
        self.login = None
        self.lock = Lock()  # Add a lock for thread safety

    def receive_target(self):
        while self._client_socket:
            try:
                msg = self._client_socket.recv(1024).decode()
                if not msg:
                    write_to_log("[ClientBL] - Server disconnected.")
                    break

                write_to_log(f"[ClientBL] - Server response: {msg}")

                # Use invokeMethod to safely update UI from another thread
                QtCore.QMetaObject.invokeMethod(
                    self.ReceiveField, "appendPlainText",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, "TEST")
                )
                write_to_log("[CClientBL] - QMetaOBject - message added to GUI")

            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def connect(self, host, port) -> socket:
        try:
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.connect((host, port))
            write_to_log(f"[CLIENT_BL] {self._client_socket.getsockname()} connected")
            return self._client_socket

        except Exception as e:
            write_to_log("[CLIENT_BL] Exception on connect: {}".format(e))
            return None

    def run(self):
        # Connect to the server
        self._host = input("Enter server IP: ")
        self._port = int(input("Enter server port: "))
        self.connect()

        # Only start threads if the connection was successful
        if self._client_socket:
            # Start sending and receiving threads
            recv_thread = Thread(target=self.receive_target)
            send_thread = Thread(target=self.send_target)
            recv_thread.start()
            send_thread.start()

            # Wait for the sending thread to stop (happens when the input is a disconnect message)
            send_thread.join()
            self.close()
        else:
            print("Failed to connect to the server. Exiting.")

    def create_message(self, message):
        return message

    def send_message(self, message):
        write_to_log(f'[ClientBL] - message received for sending: {message}')
        if self._client_socket:
            try:
                with self.lock:  # Acquire the lock
                    self._client_socket.sendall((self.create_message(message) + "\n").encode())
            except Exception as e:
                print(f"Error: {e}")

    def disconnect(self):
        if self._client_socket:
            with self.lock:  # Acquire the lock
                try:
                    write_to_log(f"[CLIENT_BL] {self._client_socket.getsockname()} closing")
                    self.send_message(DISCONNECT_MSG)
                    self._client_socket.close()
                    return True
                except Exception as e:
                    write_to_log("[CLIENT_BL] Exception on disconnect: {}".format(e))
                    return False

    def receive_target(self):
        while self._client_socket:  # Only run if the socket is valid
            try:
                msg = self._client_socket.recv(1024).decode()
                write_to_log(f"[ClientBL] - Server response: {msg}")
                if not msg:  # If the server closes the connection
                    write_to_log("[ClientBL] - Server disconnected.")
                    break
                print(f"Server: {msg}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_target(self):
        while self._client_socket:  # Only run if the socket is valid
            msg = input()
            self.send_message(msg)
            if msg.upper() == DISCONNECT_MSG:
                self.disconnect()  # Close the socket
                return


if __name__ == "__main__":
    client = CClientBL()
    client.run()