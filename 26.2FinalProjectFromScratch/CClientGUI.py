

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from CClientBL import *
from CDrawingGUI import CDrawingGUI
from CViewGUI import CViewGUI
from protocol import *
from config import *


class CClientGUI(CClientBL, object):
    def __init__(self):
        super().__init__()

        self._client_socket = None

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
        self.gridLayout.addWidget(self.IPLabel, 1, 0)
        self.gridLayout.addWidget(self.IPField, 1, 1)

        # Port label and input field
        self.PortLabel = QtWidgets.QLabel(" Port:", self.verticalLayoutWidget_2)
        self.PortField = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
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

        # Setup menu bar and status bar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

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
        # self.DrawBtn.setEnabled(False)
        # self.WatchBtn.setEnabled(False)
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

    # target functions for the buttons
    def on_click_connect(self):
        ip = self.IPField.text()
        port = int(self.PortField.text())

        self._client_socket = self.connect(ip, port)  # Ensure your connect function takes arguments

        if self._client_socket:
            self.ReceiveField.appendPlainText("Connected successfully!")  # Update UI
            self.ConnectBtn.setEnabled(False)
            self.LoginBtn.setEnabled(True)
            self.LeaveBtn.setEnabled(True)
        else:
            self.ReceiveField.appendPlainText("Failed to connect.")

    def on_click_send(self):
        text = self.SendField.text()
        write_to_log(f'[ClientGUI] message to be sent: {text}')
        self.send_message(text)

    def on_click_login(self):
        # now you cant login but can play and send messages
        self.LoginBtn.setEnabled(False)
        self.PlayBtn.setEnabled(True)
        # self.SendBtn.setEnabled(True)

    def on_click_play(self):
        pass

    def on_click_draw(self):
        self.drawing_wnd = CDrawingGUI()
        self.drawing_wnd.show()


    def on_click_watch(self):
        self.view_wnd = CViewGUI()
        self.view_wnd.show()

    def on_click_leave(self):
        pass

    def retranslateUi(self, MainWindow):
        """Handles the translation of UI elements."""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Client"))


# Run the application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = CClientGUI()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
