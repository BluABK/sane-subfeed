from PyQt5 import sip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from sane_yt_subfeed.log_handler import create_logger

from sane_yt_subfeed.controller.listeners.download_handler import DownloadHandler
from sane_yt_subfeed.gui.views.download_view.buttons.buttons_tile import ButtonsTile
from sane_yt_subfeed.gui.views.download_view.download_tile import DownloadTile


class DownloadView(QWidget):

    def __init__(self, parent, *args, **kwargs):
        super(DownloadView, self).__init__(parent, *args, **kwargs)
        self.sane_paret = parent
        self.logger = create_logger(__name__)

        self.sane_layout = QVBoxLayout()
        self.sane_layout.setAlignment(Qt.AlignTop)

        self.buttons_tile = ButtonsTile(self)

        self.sane_layout.addWidget(self.buttons_tile)

        self.setLayout(self.sane_layout)

        self.widgets = []

        DownloadHandler.static_self.newYTDLDownlaod.connect(self.new_download)

    def new_download(self, download_progress_listener):
        self.logger.info("New download signal received: {}".format(download_progress_listener.__dict__))
        widget = DownloadTile(self, download_progress_listener)
        self.widgets.append(widget)
        self.sane_layout.addWidget(widget)

    def clear_downloads(self):
        for widget in self.widgets:
            if widget.finished:
                self.logger.info("Removing widget for video: {} - {}".format(widget.video.title, widget.__dict__))
                self.sane_layout.removeWidget(widget)
                sip.delete(widget)
                self.widgets.remove(widget)
            else:
                self.logger.debug("Widget not finished: {}".format(widget.__dict__))