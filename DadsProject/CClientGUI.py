import tkinter as tk
from tkinter import *
from CClientBL import *
from CLoginGUI import *
import json
# from CProtocol26 import *
# from CProtocol27 import *
# from CProtocol import *
import CProtocol

BTN_IMAGE = "./Images/GUI - button.png"
BG_IMAGE = "./Images/GUI - BG.png"
FONT = "Calibri"
FONT_BUTTON = (FONT, 16)


class CClientGUI(CClientBL):

    def __init__(self, host, port):

        super().__init__(host, port)

        self._entry_Send_Add = None
        self._entry_Send_command = None
        self._root = tk.Tk()
        self._canvas = None
        self._img_bg = None
        self._img_btn = None

        self._entry_IP = None
        self._entry_Port = None
        self._entry_Received = None
        self._entry_Send = None

        self._btn_connect = None
        self._btn_disconnect = None
        self._btn_send = None
        self._btn_login = None

        self.create_ui()

    def create_ui(self):
        self._root.title("Client GUI")

        # Load bg image
        self._img_bg = PhotoImage(file=BG_IMAGE)
        img_width = self._img_bg.width()
        img_height = self._img_bg.height()

        # Set size of the application window = image size
        self._root.geometry(f'{img_width}x{img_height}')
        self._root.resizable(False, False)

        # Create a canvas to cover the entire window
        self._canvas = tk.Canvas(self._root, width=img_width, height=img_height)
        self._canvas.pack(fill='both', expand=True)
        self._canvas.create_image(0, 0, anchor="nw", image=self._img_bg)

        # Add labels, the same as. add text on canvas
        self._canvas.create_text(90, 50, text='Client', font=('Calibri', 28), fill='#808080')
        self._canvas.create_text(50, 130, text='IP:', font=FONT_BUTTON, fill='#000000', anchor='w')
        self._canvas.create_text(50, 180, text='Port:', font=FONT_BUTTON, fill='#000000', anchor='w')
        self._canvas.create_text(50, 230, text='Send:', font=FONT_BUTTON, fill='#000000', anchor='w')
        self._canvas.create_text(50, 280, text='Received:', font=FONT_BUTTON, fill='#000000', anchor='w')

        # Load button image
        self._img_btn = PhotoImage(file=BTN_IMAGE)
        img_btn_w = self._img_btn.width()
        img_btn_h = self._img_btn.height()

        # Button "Connect"
        self._btn_connect = tk.Button(self._canvas, text="Connect", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                      width=img_btn_w, height=img_btn_h, image=self._img_btn, bd=0,
                                      command=self.on_click_connect)
        self._btn_connect.place(x=650, y=50)

        # Button "Disconnect"
        self._btn_disconnect = tk.Button(self._canvas, text="Disconnect", font=FONT_BUTTON, fg="#c0c0c0",
                                         compound="center",
                                         width=img_btn_w, height=img_btn_h, image=self._img_btn, bd=0,
                                         command=self.on_click_disconnect, state="disabled")
        self._btn_disconnect.place(x=650, y=130)

        # Button "Send Data"
        self._btn_send = tk.Button(self._canvas, text="Send Request", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                   width=img_btn_w, height=img_btn_h, image=self._img_btn, bd=0,
                                   command=self.on_click_send, state="disabled")
        self._btn_send.place(x=650, y=210)

        self._btn_login = tk.Button(self._canvas, text="Login", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                    width=img_btn_w, height=img_btn_h, image=self._img_btn, bd=0,
                                    command=self.on_click_login, state="disabled")
        self._btn_login.place(x=650, y=290)

        # Create Entry boxes
        self._entry_IP = tk.Entry(self._canvas, width=15, font=('Calibri', 16), fg='#808080')
        self._entry_IP.insert(0, '127.0.0.1')
        self._entry_IP.place(x=200, y=118)

        self._entry_Port = tk.Entry(self._canvas, width=15, font=('Calibri', 16), fg='#808080')
        self._entry_Port.insert(0, "8822")
        self._entry_Port.place(x=200, y=168)

        self._entry_Send_command = tk.Entry(self._canvas, width=15, font=('Calibri', 16), fg='#808080')
        self._entry_Send_command.insert(0, "Command")
        self._entry_Send_command.place(x=200, y=218)

        self._entry_Send_Add = tk.Entry(self._canvas, font=('Calibri', 16), fg='#808080')
        self._entry_Send_Add.insert(0, "Additional")
        self._entry_Send_Add.place(x=375, y=218)

        self._entry_Received = tk.Text(self._canvas, width=int(img_width / 23), font=('Calibri', 16), fg='#808080')
        # self._entry_Received.insert(0, "...")
        self._entry_Received.place(x=200, y=268, height=90)

    def run(self):
        self._root.mainloop()

    def on_click_connect(self):
        self._client_socket = self.connect()
        if self._client_socket:
            self._entry_IP.config(state="disabled")
            self._entry_Port.config(state="disabled")
            self._btn_connect.config(state="disabled")
            self._btn_disconnect.config(state="normal")
            self._btn_send.config(state="normal")
            self._btn_login.config(state="normal")

    def on_click_disconnect(self):
        bres = self.disconnect()
        if bres:
            self._entry_IP.config(state="normal")
            self._entry_Port.config(state="normal")
            self._btn_connect.config(state="normal")
            self._btn_disconnect.config(state="disabled")
            self._btn_send.config(state="disabled")

    def on_click_send(self):
        cmd = self._entry_Send_command.get()
        add = self._entry_Send_Add.get()
        if add == "Additional":
            add = ""
        if cmd:
            self.send_data(CProtocol, cmd, add)
            # Use "after" to update the GUI after a short delay
            self._root.after(100, self.update_received_entry)

    def on_click_login(self):
        def callback_register(data: json):
            write_to_log(f"[CLIENT GUI] Registration - Received data from Login Wnd: {data}")
            self._entry_Send_Add.delete(0, END)
            self._entry_Send_command.delete(0, END)
            self._entry_Send_command.insert(0, "REG")
            self._entry_Send_Add.insert(0, data)
            self.on_click_send()

        def callback_signin(data: json):
            write_to_log(f"[CLIENT GUI] SignIn - Received data from Login Wnd: {data}")

        write_to_log("[CLIENT GUI] Login button pressed")
        obj = CLoginGUI(self._root, callback_register, callback_signin)
        obj.run()

    def update_received_entry(self):
        message = self.receive_data()
        self._entry_Received.insert(tk.END, message)


if __name__ == "__main__":
    client = CClientGUI(CLIENT_HOST, PORT)
    client.run()
