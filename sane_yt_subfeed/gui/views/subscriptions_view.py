import os

# from PyQt5.QtGui import QListWidgetItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QListWidget, QListWidgetItem, QHBoxLayout

from sane_yt_subfeed.config_handler import read_config


class SubscriptionsView(QWidget):
    subs = None

    def __init__(self, parent, subs, clipboard, status_bar):
        super(SubscriptionsView, self).__init__(parent)
        self.config_file = None
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.subs = subs
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        sublist = QListWidget()
        sublist2 = QListWidget()
        layout.addWidget(sublist)
        layout.addWidget(sublist2)
        # for sub in self.subs:
        sublist.addItems(self.subs)
        sublist2.addItems(reversed(self.subs))
        sublist.show()

        self.show()

