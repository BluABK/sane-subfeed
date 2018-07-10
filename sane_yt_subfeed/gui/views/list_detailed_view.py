import os

# from PyQt5.QtGui import QListWidgetItem
# from PyQt5.QtCore.Qt import ItemIsEnabled
# from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QGridLayout, QTableView

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.select_operations import get_newest_stored_videos


class SubFeedTableWidget(QTableWidget):
    header_labels = None

    def __init__(self, parent, header_labels):
        QTableWidget.__init__(self, parent)
        self.header_labels = header_labels

    def setModel(self, *args, **kwargs):
        m = QStandardItemModel()
        m.setHorizontalHeaderLabels(self.header_labels)
        # self.setModel(m)
        self.model = m


class ListDetailedView(QWidget):
    vid_limit = None
    subfeed_table = None
    videos = None

    def __init__(self, clipboard, status_bar, vid_limit=40):
        super().__init__()
        self.config_file = None
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.vid_limit = vid_limit
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        # subfeed_table = QTableWidget()

        filter_dl = read_config('Gui', 'hide_downloaded')
        self.videos = get_newest_stored_videos(self.vid_limit, filter_downloaded=filter_dl)
        self.create_table_subfeed()
        layout.addWidget(self.subfeed_table)

        self.show()

    def create_table_subfeed(self):
        m = QStandardItemModel()
        m.setHorizontalHeaderLabels(['Channel', 'Title', 'URL', 'Published', 'Description', 'Missed?', 'Dismissed?'])
        tv = QTableView()
        self.subfeed_table = SubFeedTableWidget(self, ['Channel', 'Title', 'URL', 'Published', 'Description', 'Missed?', 'Dismissed?'])
        self.subfeed_table.setModel()
        # self.subfeed_table.setHorizontalHeaderLabels(['Channel', 'Title', 'URL', 'Published', 'Description', 'Missed?', 'Dismissed?'])
        # self.subfeed_table = QTableView()
        # self.subfeed_table.setModel(m)
        self.subfeed_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.subfeed_table.setSortingEnabled(True)
        self.subfeed_table.setRowCount(len(self.videos))
        self.subfeed_table.setColumnCount(7)
        for row in range(len(self.videos)):    # row
            # print("{}, 0 = {}".format(row, self.videos[row].title))
            # for column in range(self.subfeed_table.columnCount()):  # col
                # setItem(X, Y, content)
                # print("\t{}, {} = metadata of {}, 0".format(row, column, row))
            item = QTableWidgetItem(self.videos[row].channel_title)
            # item.setFlags(QtCore.Qt.ItemIsEditable)
            self.subfeed_table.setItem(row, 0, item)

            self.subfeed_table.setItem(row, 1, QTableWidgetItem(self.videos[row].title))
            self.subfeed_table.setItem(row, 2, QTableWidgetItem(self.videos[row].url_video))
            self.subfeed_table.setItem(row, 3,
                                  QTableWidgetItem(self.videos[row].date_published.isoformat(' ').split('.')[0]))
            self.subfeed_table.setItem(row, 4, QTableWidgetItem(repr(self.videos[row].description)))
            # subfeed_table.setItem(row, column, videos[row].missed)
            self.subfeed_table.setItem(row, 5, QTableWidgetItem("Not Implemented"))   # TODO: Implement
            self.subfeed_table.setItem(row, 6, QTableWidgetItem(str(self.videos[row].downloaded)))

        # table selection change
        self.subfeed_table.doubleClicked.connect(self.on_click)

        self.subfeed_table.show()
        # return self.table

    def on_click(self):
        for currentQTableWidgetItem in self.subfeed_table.selectedItems():
            self.clipboard.setText(currentQTableWidgetItem.text())

