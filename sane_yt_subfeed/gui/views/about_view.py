# std libs
import os

# PyQt5 libs
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPainter

# Project internal libs


# Constants
OS_PATH = os.path.dirname(__file__)
IMG_PATH = os.path.join(OS_PATH, 'images')


class ExtendedQLabel(QLabel):
    p = None
    image_filename = None

    def __init__(self, parent, image_filename):
        QLabel.__init__(self, parent)
        self.image_filename = image_filename

    # Override
    def setPixmap(self, p):
        self.p = p

    def set_image(self, image_filename):
        self.image_filename = image_filename
        # self.set_tool_tip()
        self.setPixmap(QPixmap(image_filename))

    # Override
    def paintEvent(self, event):
        if self.p:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p)


class AboutView(QWidget):
    subs = None
    q_labels = []

    # noinspection PyArgumentList
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # textbox = QTextEdit()
        layout = QVBoxLayout()
        self.setLayout(layout)
        img_filename = os.path.join(IMG_PATH, 'about.png')
        img = ExtendedQLabel(self, img_filename)
        img.set_image(img_filename)
        img.show()
        self.q_labels.append(img)
        layout.addWidget(img)
        # img.setPixmap(QPixmap(img_filename))

        # img.show()

        # lbl = ExtendedQLabel(self)
        # lbl.set_image(image_filename)
        # lbl.show()
        # self.q_labels.append(lbl)
        # layout.addWidget(QLabel(image_filename))
        # layout.addWidget(lbl)

        self.show()
