import time
import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import ttk
from cryptography.fernet import Fernet
from CServerBL import *
# from CProtocol26 import *
# from CProtocol import *
# from CProtocol27 import *
import CProtocol
import sqlite3

protocol = CProtocol

BTN_IMAGE = "./Images/GUI - button.png"
BG_IMAGE = "./Images/GUI - BG Srv.png"
FONT = "Calibri"
FONT_BUTTON = (FONT, 16)


class CServerGUI(CServerBL):

    def __init__(self, host, port):
        super().__init__(host, port)

        self.tree = None
        self._client_handlers_length = len(self._client_handlers)
        # Attributes
        self._server_thread = None

        self._root = None
        self._canvas = None
        self._img_bg = None
        self._img_btn = None

        self._entry_IP = None
        self._entry_Port = None
        self._entry_Received = None
        self._entry_Send = None

        self._btn_start = None
        self._btn_stop = None
        self._btn_register = None

        # Last table index
        self._table_index = 0
        # GUI initialization
        self.create_ui()

        # self.tree = None
        # self.tree1 = None

    def create_ui(self):

        self._root = tk.Tk()
        self._root.title("Server GUI")

        # Load bg image
        self._img_bg = PhotoImage(file=BG_IMAGE)
        img_width = self._img_bg.width()
        img_height = self._img_bg.height()

        # Set size of the application window = image size
        self._root.geometry(f'{img_width}x{img_height}')
        self._root.resizable(False, False)

        # Create a canvas to cover the entire window
        self._canvas = tk.Canvas(self._root)
        self._canvas.config(width=img_width, height=img_height)
        self._canvas.pack(fill='both', expand=True)
        self._canvas.create_image(0, 0, anchor="nw", image=self._img_bg)

        # Add labels, the same as. add text on canvas
        self._canvas.create_text(90, 80, text='Server', font=('Calibri', 28), fill='#808080')
        self._canvas.create_text(50, 180, text='IP:', font=FONT_BUTTON, fill='#000000', anchor='w')
        self._canvas.create_text(50, 230, text='Port:', font=FONT_BUTTON, fill='#000000', anchor='w')
        self._canvas.create_text(50, 280, text='Send:', font=FONT_BUTTON, fill='#000000', anchor='w')
        self._canvas.create_text(50, 330, text='Received:', font=FONT_BUTTON, fill='#000000', anchor='w')

        # Load button image
        self._img_btn = PhotoImage(file=BTN_IMAGE)
        img_btn_w = self._img_btn.width()
        img_btn_h = self._img_btn.height()

        # Button "Start"
        self._btn_start = tk.Button(self._canvas, text="Start", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                    width=img_btn_w, height=img_btn_h, image=self._img_btn, bd=0,
                                    command=self.on_click_start)
        self._btn_start.place(x=650, y=50)

        # Button "Stop"
        self._btn_stop = tk.Button(self._canvas, text="Stop", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                   width=img_btn_w, height=img_btn_h, image=self._img_btn, bd=0,
                                   command=self.on_click_stop, state="disabled")
        self._btn_stop.place(x=650, y=130)

        self._btn_register = tk.Button(self._canvas, text="Register", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                       width=img_btn_w, height=img_btn_h, image=self._img_btn, bd=0,
                                       state="disabled")
        self._btn_register.place(x=650, y=210)

        # Create Entry boxes
        self._entry_IP = tk.Entry(self._canvas, font=('Calibri', 16), fg='#808080')
        self._entry_IP.insert(0, '127.0.0.1')
        self._entry_IP.place(x=200, y=168)

        self._entry_Port = tk.Entry(self._canvas, font=('Calibri', 16), fg='#808080')
        self._entry_Port.insert(0, "8822")
        self._entry_Port.place(x=200, y=218)

        self._entry_Send = tk.Entry(self._canvas, font=('Calibri', 16), fg='#808080')
        self._entry_Send.insert(0, "text message")
        self._entry_Send.place(x=200, y=268)

        self._entry_Received = tk.Entry(self._canvas, font=('Calibri', 16), fg='#808080')
        self._entry_Received.insert(0, "...")
        self._entry_Received.place(x=200, y=318)

        self.tree = ttk.Treeview(self._canvas, columns=("IP", "Address"), show="headings")
        self.tree.configure(height=5)
        self.tree.heading("IP", text="IP")
        self.tree.heading("Address", text="Address")
        self.tree.place(x=45, y=img_height - 350)

        self.tree1 = ttk.Treeview(self._canvas, columns=("IP", "Address"), show="headings")
        self.tree1.configure(height=5)
        self.tree1.heading("IP", text="IP")
        self.tree1.heading("Address", text="Address")
        self.tree1.place(x=45, y=img_height - 200)

    def run(self):
        self._root.mainloop()

    def on_click_start(self):
        self._entry_IP.config(state="disabled")
        self._entry_Port.config(state="disabled")
        self._btn_start.config(state="disabled")
        self._btn_stop.config(state="normal")
        self._btn_register.config(state="normal")
        self._server_thread = threading.Thread(target=self.start_server)
        self._server_thread.start()

    def on_click_stop(self):
        self._entry_IP.config(state="normal")
        self._entry_Port.config(state="normal")
        self._btn_start.config(state="normal")
        self._btn_stop.config(state="disabled")
        self._btn_register.config(state="disabled")
        self.stop_server()

    def fernet_func(self, data_serv):
        # Key generation
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        # Encoding data
        data = data_serv
        encrypted_data = cipher_suite.encrypt(data)

        # decoding data
        decrypted_data = cipher_suite.decrypt(encrypted_data)

        print(encrypted_data)
        print(decrypted_data)
        return [encrypted_data, key]

    def data_base(self, login, password, key):
        # Connect to DB
        conn = sqlite3.connect('MyFirstDB.db')

        # Create object cursor to execute SQL queries
        cursor = conn.cursor()

        # Create Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_table(
        id INTEGER PRIMARY KEY,
        login TEXT NOT NULL,
        password TEXT NOT NULL,
        key TEXT NOT NULL)
        ''')

        # Insert data-record
        cursor.execute('''
        INSERT INTO user_table (login, password, key) VALUES (?,?,?)
        ''', (login, password, key))

        # Data selection
        cursor.execute('SELECT * FROM user_table')
        rows = cursor.fetchall()
        for row in rows:
            write_to_log(f"[CServerGUI] DB row: {row}")

        # Confirm and save changes to DB
        conn.commit()

        # Close connection
        conn.close()

    def register(self, login, password):
        # fernet
        arr = self.fernet_func(password)
        write_to_log(f"[CServerGUI] fernet password: {arr[0]}; key: {arr[1]}")
        encrypted_passw = arr[0]
        key = arr[1]
        # data base
        self.data_base(login, encrypted_passw, key)

    def fire_event(self, enum_event: int, client_handle):

        if enum_event == NEW_CONNECTION:
            address = client_handle._address
            self.tree.insert("", tk.END, value=address)
        if enum_event == NEW_REGISTRATION:
            address = client_handle._address
            self.tree1.insert("", tk.END, value=address)
        if enum_event == CLOSE_CONNECTION:
            for item in self.tree.get_children():
                values = self.tree.item(item, 'value')
                if values and str(client_handle._address[1]) in [str(value).lower() for value in values]:
                    self.tree.delete(item)


if __name__ == "__main__":
    server = CServerGUI(CLIENT_HOST, PORT)

    server.run()
