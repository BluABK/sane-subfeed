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

        self.widgets = []

        DownloadHandler.static_self.newYTDLDownlaod.connect(self.new_download)

    def new_download(self, download_progress_listener):
        widget = DownloadTile(self, download_progress_listener)
        self.widgets.append(widget)
        self.sane_layout.addWidget(widget)
