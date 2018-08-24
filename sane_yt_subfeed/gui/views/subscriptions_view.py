import os

# from PyQt5.QtGui import QListWidgetItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QListWidget, QListWidgetItem, QHBoxLayout, \
    QTableWidgetItem, QHeaderView

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions
from sane_yt_subfeed.log_handler import create_logger


class SubscriptionsView(QWidget):
    subs = None

    def __init__(self, parent, headers=None):
        """
        SubscriptionsView, a table representation of relevant parts of the Subscriptions list
        :param parent:
        :param clipboard:
        :param status_bar:
        :param headers:
        """
        super(SubscriptionsView, self).__init__(parent)
        self.logger = create_logger(__name__)
        self.root = parent  # MainWindow
        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar

        if headers:
            self.headers = headers
        else:
            self.headers = ['ID', 'Title', 'Uploaded Videos Playlist ID', 'Description', 'Subscribed on YouTube?',
                            'Force subscription?']
        self.init_ui()

    def init_ui(self):
        """
        Initialize the UI
        :return:
        """
        self.logger.info("Initialized UI")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.get_subs()
        self.create_table_subs()
        layout.addWidget(self.subs_table)

    def create_table_subs(self):
        """
        Creates the Subscriptions list (as a list) table.
        NB: get_videos() *has* to run before this function is called.
        :return:
        """
        self.logger.info("Creating subscriptions table")
        self.subs_table = QTableWidget()
        self.subs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.subs_table.setRowCount(len(self.subs))
        self.subs_table.setColumnCount(6)

        # Set the Headers
        self.subs_table.setHorizontalHeaderLabels(self.headers)
        self.subs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.subs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.subs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        # self.subs_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.subs_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.subs_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)

        # self.subs_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # Set the tooltips to headings
        for i in range(len(self.headers)):
            self.subs_table.horizontalHeaderItem(i).setToolTip(self.headers[i])

        self.table_items = []   # FIXME: unused
        for row in range(len(self.subs)):  # row
            item = QTableWidgetItem(self.subs[row].id)
            self.table_items.append(item)
            self.subs_table.setItem(row, 0, item)
            self.subs_table.setItem(row, 1, QTableWidgetItem(self.subs[row].title))
            self.subs_table.setItem(row, 2, QTableWidgetItem(self.subs[row].playlist_id))
            self.subs_table.setItem(row, 3, QTableWidgetItem(self.subs[row].description))
            if self.subs[row].subscribed:
                self.subs_table.setItem(row, 4, QTableWidgetItem(self.subs[row].subscribed))
            else:
                self.subs_table.setItem(row, 4, QTableWidgetItem("UNSET"))
            if self.subs[row].subscribed_override:
                self.subs_table.setItem(row, 5, QTableWidgetItem(self.subs[row].subscribed_override))
            else:
                self.subs_table.setItem(row, 5, QTableWidgetItem("UNSET"))

            # Enable table sorting after the table has been populated otherwise sorting may interfere with the
            # insertion order (see setItem() for details)
            self.subs_table.setSortingEnabled(True)

        # self.subs_table.resizeColumnsToContents()

        # table selection change
        self.subs_table.doubleClicked.connect(self.on_doubleclick)

        # self.subs_table.show()

    def on_doubleclick(self):
        """
        Cell double-clicked action
        :return:
        """
        self.copy_selection_to_clipboard()

    def copy_selection_to_clipboard(self):
        """
        Copy current selection to clipboard
        :return:
        """
        for currentQTableWidgetItem in self.subs_table.selectedItems():
            self.clipboard.setText(currentQTableWidgetItem.text())

    def get_subs(self):
        """
        Retrieve Channels table from DB
        :return:
        """
        self.logger.info("Getting subscriptions")
        self.subs = get_subscriptions(read_config('Debug', 'cached_subs'))
