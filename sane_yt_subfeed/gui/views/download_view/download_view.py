import shiboken2
from PySide2.QtCore import Slot
from PySide2.QtCore import Qt
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtWidgets import QWidget, QVBoxLayout, QStyleOption, QStyle

from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.database.detached_models.d_db_download_tile import DDBDownloadTile
from sane_yt_subfeed.gui.views.download_view.buttons.buttons_tile import ButtonsTile
from sane_yt_subfeed.gui.views.download_view.download_tile import DownloadTile
from sane_yt_subfeed.handlers.log_handler import create_logger


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

        DownloadViewListener.static_self.dbDownloadTiles.connect(self.update_widgets)
        DownloadViewListener.static_self.newYTDLDownload.connect(self.new_download)

        DownloadViewListener.static_self.loadDBDownloadTiles.emit()

    def new_download(self, download_progress_listener, widget=None):
        if not widget:
            self.logger.info("New download signal received: {}".format(download_progress_listener.__dict__))
            widget = DownloadTile(self, download_progress_listener)
            DownloadViewListener.static_self.newDownloadTile.emit(DDBDownloadTile(widget))
            self.widgets.append(widget)
            self.sane_layout.addWidget(widget)
        else:
            self.logger.info("New download retry signal "
                             "received for existing widget: {}".format(download_progress_listener.__dict__))
            widget.retry(download_progress_listener)

    def clear_finished_downloads(self):
        """
        Clears all finished downloads from the list and updated DB.
        :return:
        """
        widgets_to_delete = []
        for widget in self.widgets:
            if widget.finished:
                widget.cleared = True
                DownloadViewListener.static_self.updateDownloadTile.emit(DDBDownloadTile(widget))
                widgets_to_delete.append(widget)
        while widgets_to_delete:
            widget = widgets_to_delete.pop()
            self.logger.info("Removing widget for video: {} - {}".format(widget.video.title, widget.__dict__))
            shiboken2.delete(widget)
            self.widgets.remove(widget)

    def clear_download_forced(self, widget):
        """
        Clears a download regardless of its status, and updates DB.
        :param widget:
        :return:
        """
        widget.cleared = True
        DownloadViewListener.static_self.updateDownloadTile.emit(DDBDownloadTile(widget))
        self.logger.info("Forcibly removing widget for video: {} - {}".format(widget.video.title, widget.__dict__))
        try:
            shiboken2.delete(widget)
            self.widgets.remove(widget)
        except RuntimeError as re_exc:
            if hasattr(self, 'video'):
                cur_vid = self.video
            else:
                cur_vid = "Non-existent video (nullptr)"
            if str(re_exc) == "wrapped C/C++ object of type DownloadTile has been deleted":
                self.logger.exception("Attempted to delete a nullptr widget: {}".format(cur_vid), exc_info=re_exc)
            else:
                self.logger.exception("Unexpected RuntimeError on deleting widget: {}".format(cur_vid),
                                      exc_info=re_exc)

    # noinspection PyCallingNonCallable
    @Slot(list)
    def update_widgets(self, d_db_download_til_list):
        self.logger.info("Adding loaded downloads: {}".format(d_db_download_til_list))
        for db_download_tile in d_db_download_til_list:
            if db_download_tile.video:
                widget = DownloadTile(self, db_download_tile.progress_listener, db_download_tile=db_download_tile)
                DownloadViewListener.static_self.newDownloadTile.emit(DDBDownloadTile(widget))
                self.widgets.append(widget)
                self.sane_layout.addWidget(widget)
            else:
                self.logger.warning(
                    "Download tile without video, grabbed from db: {}".format(db_download_tile.__dict__))

    def paintEvent(self, paint_event: QPaintEvent):
        """
        Override painEvent in order to support stylesheets.
        :param paint_event:
        :return:
        """
        style_option = QStyleOption()
        style_option.initFrom(self)
        painter = QPainter(self)
        style = self.style()
        style.drawPrimitive(QStyle.PE_Widget, style_option, painter, self)
