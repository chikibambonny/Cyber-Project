import socket
from threading import Thread, Lock
from config import *
from protocol import *


class CClientBL:
    def __init__(self):
        # self._host = SERVER_HOST
        # self._port = PORT
        self._client_socket = None
        self.login = None
        self.lock = Lock()  # Add a lock for thread safety
        self.text_queue = SimpleQueue()  # queue for updating the receive

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
        # self._host = input("Enter server IP: ")
        # self._port = int(input("Enter server port: "))
        # self.connect()

        # Only start threads if the connection was successful
        if self._client_socket:
            # Start sending and receiving threads
            recv_thread = Thread(target=self.receive_target)
            send_thread = Thread(target=self.send_target)
            recv_thread.start()
            send_thread.start()
            write_to_log("[CClientBL] - threads started")

            # Wait for the sending thread to stop (happens when the input is a disconnect message)
            # send_thread.join()
            # self._client_socket.close()
        else:
            print("Failed to connect to the server. Exiting.")

    def send_message(self, message):
        write_to_log(f'[ClientBL] - message received for sending: {message}')
        if self._client_socket:
            try:
                with self.lock:  # Acquire the lock
                    self._client_socket.sendall((message + "\n").encode())
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
                self.text_queue.put(msg)
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


'''
 def xxxx(self):
        def update_field_target(text_queue, field):
            while True:
                text = text_queue.get()  # Get message from queue
                if text is None:
                    return
                field.appendPlainText(text)

        text_queue=SimpleQueue()
        update_field_thread=Thread(target=update_field_target, args=(text_queue, self.ReceiveField))
        update_field_thread.start()
'''