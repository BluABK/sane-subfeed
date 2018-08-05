# PyQt5 libs
from PyQt5.QtWidgets import *

# Project internal libs
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.read_operations import get_newest_stored_videos
from sane_yt_subfeed.log_handler import create_logger


class ListDetailedView(QWidget):
    vid_limit = None
    subfeed_table = None
    table_items = None
    videos = None
    headers = None

    def __init__(self, parent, vid_limit=40, headers=None):
        """
        ListDetailedView, a table representation of relevant parts of the Subscription Feed
        :param clipboard:
        :param status_bar:
        :param vid_limit:
        """
        super(ListDetailedView, self).__init__(parent)
        self.logger = create_logger("ListDetailedView")
        self.config_file = None
        self.root = parent  # MainWindow
        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar
        self.vid_limit = vid_limit
        if headers:
            self.headers = headers
        else:
            self.headers = ['Channel', 'Title', 'URL', 'Published', 'Description', 'Missed?', 'Downloaded?',
                            'Discarded?']
        self.init_ui()

    def init_ui(self):
        """
        Initialize the UI
        :return:
        """
        self.logger.info("Initialized UI")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.get_videos()
        self.create_table_subfeed()
        layout.addWidget(self.subfeed_table)

    def create_table_subfeed(self):
        """
        Creates the Subscription Feed (as a list) table.
        NB: get_videos() *has* to run before this function is called.
        :return:
        """
        self.logger.info("Creating subfeed table")
        self.subfeed_table = QTableWidget()
        self.subfeed_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.subfeed_table.setRowCount(len(self.videos))
        self.subfeed_table.setColumnCount(8)

        # Set the Headers

        self.subfeed_table.setHorizontalHeaderLabels(self.headers)
        self.subfeed_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Title
        self.subfeed_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date

        # self.subfeed_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # Set the tooltips to headings
        for i in range(len(self.headers)):
            self.subfeed_table.horizontalHeaderItem(i).setToolTip(self.headers[i])

        self.table_items = []
        for row in range(len(self.videos)):  # row
            item = QTableWidgetItem(self.videos[row].channel_title)
            self.table_items.append(item)
            self.subfeed_table.setItem(row, 0, item)
            self.subfeed_table.setItem(row, 1, QTableWidgetItem(self.videos[row].title))
            self.subfeed_table.setItem(row, 2, QTableWidgetItem(self.videos[row].url_video))
            self.subfeed_table.setItem(row, 3,
                                       QTableWidgetItem(self.videos[row].date_published.isoformat(' ').split('.')[0]))
            self.subfeed_table.setItem(row, 4, QTableWidgetItem(self.videos[row].description))
            self.subfeed_table.setItem(row, 5, QTableWidgetItem("Not Implemented"))  # TODO: Implement missed
            self.subfeed_table.setItem(row, 6, QTableWidgetItem("Yes" if self.videos[row].downloaded else "No"))
            self.subfeed_table.setItem(row, 7, QTableWidgetItem("Yes" if self.videos[row].discarded else "No"))

            # Enable table sorting after the table has been populated otherwise sorting may interfere with the
            # insertion order (see setItem() for details)
            self.subfeed_table.setSortingEnabled(True)

        # self.subfeed_table.resizeColumnsToContents()

        # table selection change
        self.subfeed_table.doubleClicked.connect(self.on_doubleclick)

        # self.subfeed_table.show()

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
        for currentQTableWidgetItem in self.subfeed_table.selectedItems():
            self.clipboard.setText(currentQTableWidgetItem.text())

    def get_videos(self):
        """
        Retrieve a list of VideoD objects
        :return:
        """
        self.logger.info("Getting videos")
        self.videos = get_newest_stored_videos(self.vid_limit)
