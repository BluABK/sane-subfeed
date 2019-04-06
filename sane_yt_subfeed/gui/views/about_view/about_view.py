# std libs
from PyQt5.QtGui import QPixmap, QPainter
# PyQt5 libs
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

# Project internal libs
from sane_yt_subfeed.absolute_paths import ABOUT_IMG_PATH
from sane_yt_subfeed.handlers.log_handler import create_logger


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
    def __init__(self, parent):
        super(AboutView, self).__init__(parent)
        self.logger = create_logger(__name__)
        self.root = parent  # MainWindow
        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar
        self.init_ui()

    def init_ui(self):
        self.logger.info("Initializing UI: AboutView")
        # textbox = QTextEdit()
        layout = QVBoxLayout()
        self.setLayout(layout)
        img = ExtendedQLabel(self, ABOUT_IMG_PATH)
        img.set_image(ABOUT_IMG_PATH)
        # img.show()
        self.q_labels.append(img)
        layout.addWidget(img)
        # img.setPixmap(QPixmap(img_filename))

        # img.show()

        # lbl = VideoTile(self)
        # lbl.set_image(image_filename)
        # lbl.show()
        # self.q_labels.append(lbl)
        # layout.addWidget(QLabel(image_filename))
        # layout.addWidget(lbl)
