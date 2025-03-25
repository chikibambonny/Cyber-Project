from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QMainWindow)
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt
import sys


# Mock client class (replace with your actual CClientBL)
class CClientBL:
    def __init__(self):
        self.translations = {"hello": "hola", "world": "mundo"}

    def translate(self, text, target_language="es"):
        words = text.lower().split()
        translated = [self.translations.get(word, word) for word in words]
        return " ".join(translated)


class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = QPixmap(400, 300)
        self.canvas.fill(Qt.white)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas)


class CTranslationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Drawing Translator")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title label
        self.title_label = QLabel("Drawing Translation Tool")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Translation button
        self.translate_btn = QPushButton("Translate Current Drawing")
        self.translate_btn.clicked.connect(self.translate_drawing)
        layout.addWidget(self.translate_btn)

        # Result display
        self.result_label = QLabel("Translation will appear here")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        self.setLayout(layout)
        self.setStyleSheet("""
            background-color: #F5F5DC;
            QLabel { margin: 10px; }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)

    def translate_drawing(self):
        if self.parent and hasattr(self.parent, 'frameCanvas'):
            # In a real app, you'd process the actual drawing
            # For demo, we'll use a mock translation
            mock_text = "hello world"  # Replace with OCR in real implementation
            if hasattr(self.parent, 'client'):
                translated = self.parent.client.translate(mock_text)
                self.result_label.setText(f"Translated to Spanish:\n{translated}")
            else:
                self.result_label.setText("Client translation service not available")
        else:
            self.result_label.setText("No parent window with drawing found")


class CDrawingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing App")
        self.client = CClientBL()  # Mock client
        self.init_ui()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Drawing canvas
        self.frameCanvas = DrawingCanvas()
        layout.addWidget(self.frameCanvas)

        # Buttons
        btn_layout = QVBoxLayout()

        self.translate_btn = QPushButton("Open Translator")
        self.translate_btn.clicked.connect(self.open_translation_window)
        btn_layout.addWidget(self.translate_btn)

        layout.addLayout(btn_layout)
        central_widget.setLayout(layout)

        # Window size
        self.setGeometry(100, 100, 600, 500)

        # Style
        self.setStyleSheet("""
            background-color: #F5F5DC;
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                margin: 5px;
                border-radius: 4px;
            }
        """)

    def open_translation_window(self):
        self.translation_window = CTranslationWindow(self)
        self.translation_window.show()


def main():
    app = QApplication(sys.argv)

    # Create main window
    main_window = CDrawingGUI()
    main_window.show()

    # Start application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()