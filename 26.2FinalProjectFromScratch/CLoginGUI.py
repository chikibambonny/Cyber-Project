from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit,QPushButton, QVBoxLayout, QHBoxLayout
import sys
from protocol import *
from config import *
from CClientBL import *
import CClientBL

class CLoginGUI(QDialog):
    def __init__(self, client):
        super().__init__()

        self.client = client

        self.setWindowTitle("Login")
        self.setStyleSheet(f'background-color: {LIGHTBEIGE_BG};')

        # --- Username ---
        self.UsernameLabel = QLabel("Username")
        self.UsernameField = QLineEdit()
        self.UsernameField.setPlaceholderText("Enter your username")

        # --- Password ---
        self.PasswordLabel = QLabel("Password")
        self.PasswordField = QLineEdit()
        self.PasswordField.setEchoMode(QLineEdit.Password)
        self.PasswordField.setPlaceholderText("Enter your password")

        # --- Buttons ---
        self.LoginBtn = QPushButton("Log In")
        self.SignUpBtn = QPushButton("Sign Up")

        # Set object names (for styling or later use)
        self.LoginBtn.setObjectName("loginButton")
        self.SignUpBtn.setObjectName("signupButton")

        # Connect buttons
        self.LoginBtn.clicked.connect(self.handle_login)
        self.SignUpBtn.clicked.connect(self.handle_signup)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)  # adds space around the edges
        layout.setSpacing(15)  # optional: more space between widgets

        layout.addWidget(self.UsernameLabel)
        layout.addWidget(self.UsernameField)
        layout.addWidget(self.PasswordLabel)
        layout.addWidget(self.PasswordField)
        layout.addSpacing(25)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.LoginBtn)
        button_layout.addWidget(self.SignUpBtn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        Buttons = [self.LoginBtn, self.SignUpBtn]
        Fields = [self.UsernameField, self.PasswordField]
        Labels = [self.UsernameLabel, self.PasswordLabel]
        set_designs(Buttons, Fields, Labels)

    def handle_login(self):
        username = self.UsernameField.text()
        password = self.PasswordField.text()
        write_to_log(f"[Login GUI] - handle login - login attempt: {username}, {password}")
        self.client.send_message(LOGIN_ACTION, (username, password))
        write_to_log(f"[Login GUI] - handle login - message sent")

    def handle_signup(self):
        print("Sign up button clicked")
        username = self.UsernameField.text()
        password = self.PasswordField.text()
        write_to_log(f"[Login GUI] - handle signup - sign up attempt: {username}, {password}")
        self.client.send_message(SIGNUP_ACTION, (username, password))
        write_to_log(f"[Login GUI] - handle signup - message sent")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = CLoginGUI()
    if dialog.exec_():
        write_to_log("Login dialog accepted")
    else:
        write_to_log("Login dialog cancelled")
