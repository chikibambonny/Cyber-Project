from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint

import os
from datetime import datetime
from PyQt5.QtCore import QTimer

from protocol import *
from config import *
from CClientBL import *


class DrawingCanvas(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(BLACK)
        self.pen_width = 3
        self.eraser_mode = False
        self.canvas = QPixmap(self.width(), self.height())
        self.canvas.fill(Qt.white)
        self.setMouseTracking(True)

        # for smart save
        self.has_unsaved_changes = False
        # Initialize blank canvas for comparison
        self.blank_canvas = QPixmap(self.width(), self.height())
        self.blank_canvas.fill(Qt.white)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.canvas)
            if self.eraser_mode:
                painter.setPen(QPen(Qt.white, self.pen_width * 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            else:
                painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            current_point = event.pos()
            painter.drawLine(self.last_point, current_point)
            self.last_point = current_point
            self.update()
            self.has_unsaved_changes = True
            write_to_log(f'[DrawingGUI] - mouse moved has changes - {self.has_unsaved_changes}')

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def clear_canvas(self):
        self.canvas.fill(Qt.white)
        self.update()
        if not self.is_canvas_blank():  # Only mark changes if actually clearing
            self.has_unsaved_changes = True
            write_to_log(f'[DrawingGUI] - clear canvas has changes - {self.has_unsaved_changes}')

    def resizeEvent(self, event):
        # Create new pixmaps with the new size
        new_pixmap = QPixmap(event.size())  # For the drawing canvas
        new_blank = QPixmap(event.size())  # For the blank reference

        # Initialize them both as white
        new_pixmap.fill(Qt.white)
        new_blank.fill(Qt.white)

        # Copy existing drawing content (if any)
        painter = QPainter(new_pixmap)
        painter.drawPixmap(0, 0, self.canvas)
        painter.end()

        # Update our references
        self.canvas = new_pixmap  # Our main drawing surface
        self.blank_canvas = new_blank  # Our reference blank canvas

    # smart save functions
    def is_canvas_blank(self):
        """Compare current canvas with blank canvas"""
        return self.canvas.toImage() == self.blank_canvas.toImage()

    def save_drawing(self, folder="saved_drawings"):
        """Save only if there are changes"""
        if not self.has_unsaved_changes:
            return None

        if not os.path.exists(folder):
            os.makedirs(folder)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(folder, f"drawing_{timestamp}.png")
        self.canvas.save(filename, "PNG")
        self.has_unsaved_changes = False
        return filename


class CDrawingGUI(CClientBL, QtWidgets.QWidget):
    def __init__(self):
        # Initialize QWidget first (the graphical base)
        QtWidgets.QWidget.__init__(self)
        # Then initialize CClientBL
        CClientBL.__init__(self)

        # Drawing attributes
        self.eraser_mode = False

        # palette
        self.RedBtn = None
        self.OrangeBtn = None
        self.YellowBtn = None
        self.GreenBtn = None
        self.BlueBtn = None
        self.PurpleBtn = None
        self.PinkBtn = None
        self.BlackBtn = None

        # buttons
        self.EraserBtn = None
        self.ClearBtn = None

        self.setupUi(self)
        self.setup_autosave()

    def setup_autosave(self):
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_drawing)
        write_to_log(f'[DrawingGUI] - saving - timeout set')
        self.autosave_timer.start(10 * 1000)  # 5 minutes in milliseconds 5 * 60 * 1000

    def autosave_drawing(self):
        filename = self.frameCanvas.save_drawing()
        write_to_log(f"Auto-saved drawing to: {filename}")  # Optional logging

    def setupUi(self, Form):
        Form.setObjectName("Drawing")
        Form.resize(657, 388)

        # Create the drawing canvas
        self.frameCanvas = DrawingCanvas(Form)
        self.frameCanvas.setGeometry(QtCore.QRect(30, 70, 481, 281))
        self.frameCanvas.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameCanvas.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameCanvas.setObjectName("frameCanvas")

        # Create a QWidget to hold the color buttons and other controls
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(540, 90, 91, 174))
        self.widget.setObjectName("widget")

        # Create a vertical layout to organize widgets inside the widget
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # Create a grid layout to arrange color buttons in a grid
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        # set color picking buttons
        for i, color in enumerate(PALETTE_COLORS):
            btn = QtWidgets.QPushButton()
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            btn.setFixedSize(30, 20)
            btn.clicked.connect(lambda checked, col=color: self.set_pen_color(col))
            self.gridLayout.addWidget(btn, i // 2, i % 2)

        self.verticalLayout_2.addLayout(self.gridLayout)

        # Create another vertical layout for buttons like Eraser and Clear Canvas
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # Create an Eraser button and add it to the layout
        self.EraserBtn = QtWidgets.QPushButton(self.widget)
        self.EraserBtn.setObjectName("EraserBtn")
        self.EraserBtn.clicked.connect(self.toggle_eraser)
        self.verticalLayout.addWidget(self.EraserBtn)

        # Create a Clear Canvas button and add it to the layout
        self.ClearBtn = QtWidgets.QPushButton(self.widget)
        self.ClearBtn.setObjectName("pushButton_10")
        self.ClearBtn.clicked.connect(self.clear_canvas)
        self.verticalLayout.addWidget(self.ClearBtn)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # set style
        buttons = [self.ClearBtn, self.EraserBtn]
        fields = [self.frameCanvas]
        labels = []
        set_designs(buttons, fields, labels)
        Form.setStyleSheet(f"background-color: {LIGHTBEIGE_BG};")

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Draw"))
        self.EraserBtn.setText(_translate("Form", "Eraser"))
        self.ClearBtn.setText(_translate("Form", "Clear canvas"))

    def set_pen_color(self, color):
        """Set the pen color from an 'rgb(r,g,b)' string"""
        # Extract numbers from "rgb(192, 57, 53)" format
        if color.startswith("rgb(") and color.endswith(")"):

            rgb_values = color[4:-1].split(',')  # Gets ["192", " 57", " 53"]
            write_to_log(f'[DrawingGUI] - set_pen_color - rgb values{rgb_values}')
            r = int(rgb_values[0])  # Convert to integers
            g = int(rgb_values[1])
            b = int(rgb_values[2])
            self.frameCanvas.pen_color = QColor(r, g, b)
        else:
            # Fallback for other formats (hex, color names, etc)
            self.frameCanvas.pen_color = QColor(color)

        self.frameCanvas.eraser_mode = False
        self.EraserBtn.setStyleSheet("")  # Reset eraser button style

    def toggle_eraser(self):
        self.frameCanvas.eraser_mode = not self.frameCanvas.eraser_mode
        if self.frameCanvas.eraser_mode:
            self.EraserBtn.setStyleSheet(f"""background-color: {DIS_BUTTONS};  
        color: {TEXT_BUTTONS};
        border: 2px solid {DIS_BORDER_BUTTONS};  /* Softer border for disabled buttons */
        border-bottom: 4px solid {DIS_SHADOW_BUTTONS};  /* Softer shadow for disabled buttons */
        border-radius: 8px;
            """)
        else:
            self.EraserBtn.setStyleSheet(f"""
background-color: {BUTTONS};  
        color: {TEXT_BUTTONS};
        border: 2px solid {BORDER_BUTTONS};  /* Main border */
        border-bottom: 4px solid {SHADOW_BUTTONS};  /* Simulated shadow at the bottom */
        border-radius: 8px;
""")

    def clear_canvas(self):
        self.frameCanvas.clear_canvas()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = CDrawingGUI()
    window.show()
    sys.exit(app.exec_())