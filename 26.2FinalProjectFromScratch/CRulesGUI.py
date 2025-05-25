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

        layout = QVBoxLayout()

        rules_label = QLabel("""
                <h2>Welcome to the Charades Game!</h2>
                <ul>
                <li>Once you click on Play, the game starts</li>
                <li>You can choose themes in the dropdown menu</li>
                <li>The artist is chosen randomly</li>
                <li>The artist receives a word and has to draw it</li>
                <li>Other players has to guess the word in the chat</li>
                <li>For now log in isn't mandatory, however we're planning on adding rating system later, so we highly recommend on using your accounts</li>
                <li></li>
                <li>No writing words, letters, or numbers in the drawing!</li>
                <li>Be respectful and have fun 🎨✨</li>
                </ul>
                """)
        rules_label.setAlignment(Qt.AlignTop)
        rules_label.setWordWrap(True)
        rules_label.setTextFormat(Qt.RichText)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        layout.addWidget(rules_label)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        set_designs([close_button], [], [rules_label])

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the window
    wnd = CRulesGUI()
    wnd.show()

    # Run the application
    sys.exit(app.exec_())


