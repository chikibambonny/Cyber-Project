import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import base64

from protocol import *
from config import *
from CClientBL import *


class CViewGUI(CClientBL, QWidget):
    def __init__(self):
        # Initialize QWidget first (the graphical base)
        QWidget.__init__(self)
        # Then initialize CClientBL
        CClientBL.__init__(self)

        self.setWindowTitle("View")
        self.setGeometry(100, 100, 601, 301)  # Window size
        self.setStyleSheet(f'background-color: {LIGHTBEIGE_BG};')

        # Create main layout with margins (left, top, right, bottom)
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.setContentsMargins(40, 30, 40, 30)  # 40px sides, 30px top/bottom
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Image label with fixed display size
        self.image_label = QLabel()
        self.image_label.setFixedSize(481, 281)  # Your specific image display size
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.layout.addWidget(self.image_label, 0, Qt.AlignCenter)

        # Load your translated image
        # self.load_translated_image(CAST_IMG_PATH)

    def update_image_from_base64(self, img_b64):
        img_bytes = base64.b64decode(img_b64)
        image = QtGui.QImage.fromData(img_bytes)
        pixmap = QtGui.QPixmap.fromImage(image)
        scaled = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)

    def load_translated_image(self, image_path):
        """Load image with specific display constraints"""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Scale to fit the label while preserving aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            print("Error loading translated image")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the window
    viewer = CViewGUI()
    viewer.show()

    # Run the application
    sys.exit(app.exec_())