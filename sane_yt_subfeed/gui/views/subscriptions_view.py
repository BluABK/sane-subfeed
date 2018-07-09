import os

# from PyQt5.QtGui import QListWidgetItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QListWidget, QListWidgetItem

from sane_yt_subfeed.config_handler import read_config


class SubscriptionsView(QWidget):
    subs = None

    def __init__(self, subs, clipboard, status_bar):
        super().__init__()
        self.config_file = None
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.subs = subs
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        subtable = QListWidget()
        layout.addWidget(subtable)
        # for sub in self.subs:
        subtable.addItems(self.subs)
        subtable.show()

        self.show()

