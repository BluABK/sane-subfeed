from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from sane_yt_subfeed.controller.listeners.download_handler import DownloadHandler
from sane_yt_subfeed.gui.views.download_view.download_tile import DownloadTile


class DownloadView(QWidget):

    def __init__(self, parent, *args, **kwargs):
        super(DownloadView, self).__init__(parent, *args, **kwargs)
        self.sane_paret = parent

        self.sane_layout = QVBoxLayout()
        self.sane_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.sane_layout)

        self.test_widget = DownloadTile(self, "")
        self.sane_layout.addWidget(self.test_widget)
        DownloadHandler.static_self.newYTDLDownlaod.connect(self.new_download)

    def new_download(self):
        print("hello world")
