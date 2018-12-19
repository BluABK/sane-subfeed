from PyQt5 import sip
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from sane_yt_subfeed.controller.listeners.download_handler import DownloadHandler
from sane_yt_subfeed.database.detached_models.d_db_download_tile import DDBDownloadTile
from sane_yt_subfeed.gui.views.download_view.buttons.buttons_tile import ButtonsTile
from sane_yt_subfeed.gui.views.download_view.download_tile import DownloadTile
from sane_yt_subfeed.log_handler import create_logger


class DownloadView(QWidget):

    def __init__(self, parent, *args, **kwargs):
        super(DownloadView, self).__init__(parent, *args, **kwargs)
        self.root = parent.root
        self.parent = parent
        self.logger = create_logger(__name__)

        self.sane_layout = QVBoxLayout()
        self.sane_layout.setAlignment(Qt.AlignTop)

        self.buttons_tile = ButtonsTile(self)

        self.sane_layout.addWidget(self.buttons_tile)

        self.setLayout(self.sane_layout)

        self.widgets = []

        DownloadHandler.static_self.dbDownloadTiles.connect(self.update_widgets)
        DownloadHandler.static_self.newYTDLDownlaod.connect(self.new_download)

        DownloadHandler.static_self.loadDBDownloadTiles.emit()
        # # FIXME: remove and fix signals instead
        # db_downloads = db_session.query(DBDownloadTile).filter(DBDownloadTile.cleared == false())
        # for download in db_downloads:
        #     self.new_download(download, emit_signal=False)

    def new_download(self, download_progress_listener):
        self.logger.info("New download signal received: {}".format(download_progress_listener.__dict__))
        widget = DownloadTile(self, download_progress_listener)
        DownloadHandler.static_self.newDownloadTile.emit(DDBDownloadTile(widget))
        self.widgets.append(widget)
        self.sane_layout.addWidget(widget)

    def clear_finished_downloads(self):
        """
        Clears all finished downloads from the list and updated DB.
        :return:
        """
        widgets_to_delete = []
        for widget in self.widgets:
            if widget.finished:
                widget.cleared = True
                DownloadHandler.static_self.updateDownloadTile.emit(DDBDownloadTile(widget))
                widgets_to_delete.append(widget)
            else:
                self.logger.debug("Widget not finished: {}".format(widget.__dict__))
        while widgets_to_delete:
            widget = widgets_to_delete.pop()
            self.logger.info("Removing widget for video: {} - {}".format(widget.video.title, widget.__dict__))
            sip.delete(widget)
            self.widgets.remove(widget)

    def clear_download_forced(self, widget):
        """
        Clears a download regardless of its status, and updates DB.
        :param widget:
        :return:
        """
        widget.cleared = True
        DownloadHandler.static_self.updateDownloadTile.emit(DDBDownloadTile(widget))
        self.logger.info("Forcibly removing widget for video: {} - {}".format(widget.video.title, widget.__dict__))
        sip.delete(widget)
        self.widgets.remove(widget)

    @pyqtSlot(list)
    def update_widgets(self, d_db_download_til_list):
        self.logger.info("Adding loaded downloads: {}".format(d_db_download_til_list))
        for db_download_tile in d_db_download_til_list:
            if db_download_tile.video:
                widget = DownloadTile(self, db_download_tile.progress_listener, db_download_tile=db_download_tile)
                DownloadHandler.static_self.newDownloadTile.emit(DDBDownloadTile(widget))
                self.widgets.append(widget)
                self.sane_layout.addWidget(widget)
            else:
                self.logger.warning(
                    "Download tile without video, grabbed from db: {}".format(db_download_tile.__dict__))
