from PyQt5 import QtCore, QtGui, QtWidgets
import sys

from PyQt5.QtCore import QTimer

from CClientBL import *
from CDrawingGUI import CDrawingGUI
from CViewGUI import CViewGUI
from CLoginGUI import CLoginGUI
from protocol import *
from config import *
from queue import SimpleQueue


class CClientGUI(CClientBL, object):
    def __init__(self):
        super().__init__()

        self._client_socket = None
        self.receive_update_thread = None
        self.gui_updates = None

        self.view_wnd = None
        self.drawing_wnd = None

        # fields
        self.IPField = None
        self.PortField = None
        self.ReceiveField = None
        self.SendField = None

        # buttons
        self.ConnectBtn = None
        self.SendBtn = None
        self.LoginBtn = None
        self.PlayBtn = None
        self.DrawBtn = None
        self.WatchBtn = None
        self.LeaveBtn = None
        # labels
        self.IPLabel = None
        self.PortLabel = None
        self.ReceiveLabel = None
        self.SendLabel = None

        # Timer to process the queue in the main thread
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_gui_queue)
        self.timer.start(50)

    def setupUi(self, MainWindow):
        """Sets up the UI for the main window."""

        # Configure main window properties
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(950, 600)  # Increased window size for better spacing

        # Set background color for the main window
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(251, 246, 227))  # Light beige background color
        brush.setStyle(QtCore.Qt.SolidPattern)

        # Apply background color to different UI states
        for state in [QtGui.QPalette.Active, QtGui.QPalette.Inactive, QtGui.QPalette.Disabled]:
            palette.setBrush(state, QtGui.QPalette.Button, brush)
            palette.setBrush(state, QtGui.QPalette.Base, brush)
            palette.setBrush(state, QtGui.QPalette.Window, brush)

        # Apply the palette to the main window
        MainWindow.setPalette(palette)
        MainWindow.setStyleSheet(f"background-color: {LIGHTBEIGE_BG};")

        # Create central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # --- LAYOUT 2 (Connection Fields) --- (Moved up & left, increased size)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(50, 190, 360, 270))  # Adjusted position & size
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)

        # Create grid layout for input fields
        self.gridLayout = QtWidgets.QGridLayout()

        # IP Address label and input field
        self.IPLabel = QtWidgets.QLabel(" IP Address:", self.verticalLayoutWidget_2)
        self.IPField = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.IPField.setText(SERVER_HOST)  # set default value
        self.gridLayout.addWidget(self.IPLabel, 1, 0)
        self.gridLayout.addWidget(self.IPField, 1, 1)

        # Port label and input field
        self.PortLabel = QtWidgets.QLabel(" Port:", self.verticalLayoutWidget_2)
        self.PortField = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.PortField.setText(str(PORT))  # set default value
        self.gridLayout.addWidget(self.PortLabel, 2, 0)
        self.gridLayout.addWidget(self.PortField, 2, 1)

        # Connect button
        self.ConnectBtn = QtWidgets.QPushButton("  Connect  ", self.verticalLayoutWidget_2)
        self.gridLayout.addWidget(self.ConnectBtn, 1, 2, 2, 1)

        # Add grid layout to vertical layout
        self.verticalLayout_2.addLayout(self.gridLayout)

        # --- MESSAGE SENDING & RECEIVING SECTION ---
        self.ReceiveLabel = QtWidgets.QLabel(" Receive:", self.verticalLayoutWidget_2)
        self.ReceiveField = QtWidgets.QPlainTextEdit(self.verticalLayoutWidget_2)

        # Add Receive section to layout
        self.verticalLayout_2.addWidget(self.ReceiveLabel)
        self.verticalLayout_2.addWidget(self.ReceiveField)

        # Create "Send" messages section
        self.Sendlabel = QtWidgets.QLabel(" Send:", self.verticalLayoutWidget_2)
        self.SendField = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.SendBtn = QtWidgets.QPushButton("  Send  ", self.verticalLayoutWidget_2)

        # Horizontal layout for send message field and button
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.addWidget(self.SendField)
        self.horizontalLayout_3.addWidget(self.SendBtn)

        # Add Send section to layout
        self.verticalLayout_2.addWidget(self.Sendlabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        # --- LAYOUT 1 (Buttons) --- (Moved right, increased size)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(620, 300, 260, 160))  # Adjusted position & size
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # Create buttons
        self.LoginBtn = QtWidgets.QPushButton(" Login ", self.verticalLayoutWidget)
        self.PlayBtn = QtWidgets.QPushButton(" Play ", self.verticalLayoutWidget)
        self.DrawBtn = QtWidgets.QPushButton(" Draw ", self.verticalLayoutWidget)
        self.WatchBtn = QtWidgets.QPushButton(" Watch ", self.verticalLayoutWidget)
        self.LeaveBtn = QtWidgets.QPushButton(" Leave ", self.verticalLayoutWidget)

        # Add buttons to layout
        self.verticalLayout.addWidget(self.LoginBtn)
        self.verticalLayout.addWidget(self.PlayBtn)

        # Create horizontal layout for "Draw" and "Watch" buttons
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addWidget(self.DrawBtn)
        self.horizontalLayout.addWidget(self.WatchBtn)

        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.LeaveBtn)

        # Finalize main window setup
        MainWindow.setCentralWidget(self.centralwidget)

        # Apply translations for UI elements
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # --- APPLY STYLES TO BUTTONS AND INPUT FIELDS ---
        # List of all buttons
        buttons = [
            self.ConnectBtn, self.LoginBtn, self.PlayBtn, self.DrawBtn,
            self.WatchBtn, self.LeaveBtn, self.SendBtn
        ]
        # List of all input fields
        input_fields = [
            self.IPField, self.PortField, self.SendField, self.ReceiveField
        ]
        # list of all labels
        labels = [
            self.IPLabel, self.PortLabel, self.ReceiveLabel, self.Sendlabel
        ]
        set_designs(buttons, input_fields, labels)


        # SET UP DEFAULT STATES
        self.ConnectBtn.setEnabled(True)
        self.LoginBtn.setEnabled(False)
        self.PlayBtn.setEnabled(False)
        self.DrawBtn.setEnabled(False)
        self.WatchBtn.setEnabled(False)
        self.LeaveBtn.setEnabled(False)
        self.SendBtn.setEnabled(True)

        self.IPField.setReadOnly(False)
        self.PortField.setReadOnly(False)
        self.SendField.setReadOnly(False)
        self.ReceiveField.setReadOnly(True)

        # declare target functions of buttons
        # Connect buttons to functions
        self.ConnectBtn.clicked.connect(self.on_click_connect)
        self.LoginBtn.clicked.connect(self.on_click_login)
        self.PlayBtn.clicked.connect(self.on_click_play)
        self.DrawBtn.clicked.connect(self.on_click_draw)
        self.WatchBtn.clicked.connect(self.on_click_watch)
        self.LeaveBtn.clicked.connect(self.on_click_leave)
        self.SendBtn.clicked.connect(self.on_click_send)

    # process gui updating queue
    def process_gui_queue(self):
        if self.gui_updates:
            while not self.gui_updates.empty():
                func, args, kwargs = self.gui_updates.get()
                func(*args, **kwargs)

    def receive_update_target(self, text_queue, field):
        while True:
            text = text_queue.get()  # Get message from queue
            write_to_log(f'[ClientGUI] - update target - got from queue: {text}')
            if text is None:
                return
            action, parsed_text = text.split(ACT_DELIMITER)
            if action == TEXT_ACTION:
                self.gui_updates.put((self.append_field, (self.ReceiveField, parsed_text), {}))
            elif action == ROLE_ACTION:
                write_to_log(f'[ClientGUI] - update target - Role :{repr(parsed_text), repr(str(DRAW_ROLE))}')
                if parsed_text == str(DRAW_ROLE):
                    self.gui_updates.put((self.set_ability, (self.DrawBtn, True), {}))
                    self.gui_updates.put((self.append_field, (self.ReceiveField, 'Time to draw!'), {}))
                    write_to_log(f'[ClientGUI] - update target - role updates ran')
                elif parsed_text == str(GUESS_ROLE):
                    self.gui_updates.put((self.set_ability, (self.DrawBtn, False), {}))
                    self.gui_updates.put((self.append_field, (self.ReceiveField, 'Time to guess!'), {}))
                    self.gui_updates.put((self.close_drawing, (), {}))
                    write_to_log(f'[ClientGUI] - update target - role updates ran')
            elif action == WORD_ACTON:
                self.gui_updates.put((self.append_field, (self.ReceiveField, f'Your word to draw is: {parsed_text}'), {}))
            elif action == IMAGE_ACTION:
                write_to_log(f'[ClientGUI] - update target - image action')
                self.gui_updates.put((self.ensure_view_window_and_show_image, (parsed_text,), {}))
                write_to_log('[ClientGUI] - update target - image put into gui queue')
            else:
                self.gui_updates.put((self.append_field, (self.ReceiveField, text), {}))

    def on_click_connect(self):
        ip = self.IPField.text()
        port = int(self.PortField.text())

        self._client_socket = self.connect(ip, port)  # Ensure your connect function takes arguments

        # if connected
        if self._client_socket:
            self.ConnectBtn.setEnabled(False)
            self.LoginBtn.setEnabled(True)
            self.LeaveBtn.setEnabled(True)
            self.PlayBtn.setEnabled(True)
            self.WatchBtn.setEnabled(True)

            self.run()  # run client bl
            # queue for gui updates
            self.gui_updates = SimpleQueue()
            # receive updating thread
            self.receive_update_thread = Thread(target=self.receive_update_target,
                                              args=(self.text_queue, self.ReceiveField))
            self.receive_update_thread.start()

        else:
            self.ReceiveField.appendPlainText("Failed to connect.")

    def on_click_send(self):
        text = self.SendField.text()
        write_to_log(f'[ClientGUI] message to be sent: {text}')
        self.send_message(TEXT_ACTION, text)
        self.SendField.clear()

    def on_click_login(self):
        # now you cant login but can play and send messages
        self.LoginBtn.setEnabled(False)
        self.PlayBtn.setEnabled(True)
        # self.SendBtn.setEnabled(True)
        self.login_wnd = CLoginGUI(self)
        if self.login_wnd.exec_():  # Show the dialog and wait for it to close
            write_to_log("Login window used")
        else:
            write_to_log("Login canceled")

    def on_click_play(self):
        write_to_log(f'[ClientGUI] - play button clicked')
        self.send_message(PLAY_ACTION, 'play')  # it doesnt cae about play data anyways, but exit command gets triggered by empty data

    def on_click_draw(self):
        self.drawing_wnd = CDrawingGUI(self)
        self.drawing_wnd.show()

    def on_click_watch(self):
        self.view_wnd = CViewGUI()
        self.view_wnd.show()

    def on_click_leave(self):
        self.send_message(EXIT_ACTION)
        self.ConnectBtn.setEnabled(True)

    def retranslateUi(self, MainWindow):
        """Handles the translation of UI elements."""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Client"))

    # ========= UI update functions ==========
    def set_ability(self, button, value: bool):
        button.setEnabled(value)

    def append_field(self, field, text: str):
        field.appendPlainText(text)

    def close_drawing(self):
        if self.drawing_wnd:
            self.drawing_wnd.shutdown()
            self.drawing_wnd = None

    def ensure_view_window_and_show_image(self, image_b64):
        if not self.view_wnd or not self.view_wnd.isVisible():
            self.view_wnd = CViewGUI()
            self.view_wnd.show()
        self.view_wnd.update_image_from_base64(image_b64)


# Run the application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = CClientGUI()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())