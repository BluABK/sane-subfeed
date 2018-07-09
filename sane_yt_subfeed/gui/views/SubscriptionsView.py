import os
import time

from PyQt5.Qt import QClipboard
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QBasicTimer
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QAction, qApp, \
    QMenu, QGridLayout, QProgressBar, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QTextEdit
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter

from sane_yt_subfeed.config_handler import read_config


class SubscriptionsView(QWidget):
    config_file = None

    def __init__(self, clipboard, status_bar):
        super().__init__()
        self.config_file = None
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.init_ui()

    def init_ui(self):
        # textbox = QTextEdit()
        layout = None