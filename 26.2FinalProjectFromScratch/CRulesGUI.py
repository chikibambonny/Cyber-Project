import sys

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt

from config import *


class CRulesGUI(QWidget):
    def __init__(self):
        # Initialize QWidget first (the graphical base)
        QWidget.__init__(self)

        self.setWindowTitle("Rules")
        self.setGeometry(100, 100, 601, 301)  # Window size
        self.setStyleSheet(f'background-color: {LIGHTBEIGE_BG};')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the window
    wnd = CRulesGUI()
    wnd.show()

    # Run the application
    sys.exit(app.exec_())


