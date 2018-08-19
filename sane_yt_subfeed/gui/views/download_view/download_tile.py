from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QGridLayout, QProgressBar, QWidget, QSizePolicy, QMenu
from sane_yt_subfeed.controller.listeners.download_handler import DownloadHandler
from sane_yt_subfeed.database.detached_models.d_db_download_tile import DDBDownloadTile

from sane_yt_subfeed.gui.views.download_view.progress_bar import DownloadProgressBar
from sane_yt_subfeed.gui.views.download_view.small_label import SmallLabel
from sane_yt_subfeed.log_handler import create_logger

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.download_view.download_thumbnail import DownloadThumbnailWidget


class DownloadTile(QWidget):
    def __init__(self, parent, download_progress_listener, db_download_tile=None, *args, **kwargs):
        super(DownloadTile, self).__init__(parent, *args, **kwargs)
        self.logger = create_logger(__name__)
        self.logger.debug("Starting init")
        self.sane_paret = parent
        self.download_progress_listener = download_progress_listener
        self.video = download_progress_listener.video
        self.total_bytes = None
        self.video_downloaded = False
        self.finished = False
        self.finished_date = None
        self.started_date = None
        self.last_event = None
        self.cleared = False

        self.setFixedHeight(read_config('DownloadView', 'download_tile_height'))

        self.sane_layout = QGridLayout()
        # self.sane_layout.setAlignment(Qt.AlignLeading)
        self.sane_layout.setContentsMargins(0, 1, 10, 0)
        # self.setContentsMargins(0, 1, 50, 0)

        self.title_bar = SmallLabel(self.video.title, parent=self)
        self.thumbnail = DownloadThumbnailWidget(self, self.video)
        self.progress_bar = DownloadProgressBar(self)
        # self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.status = SmallLabel("Status:", parent=self)
        self.duration = SmallLabel("Duration:", parent=self)
        self.upload = SmallLabel("Uploaded:", parent=self)
        self.eta = SmallLabel("ETA:", parent=self)
        self.speed = SmallLabel("Speed:", parent=self)
        self.total_size = SmallLabel("Total size:", parent=self)

        self.status_value = SmallLabel("No update", parent=self)
        self.duration_value = SmallLabel("Not Implemented", parent=self)
        self.upload_value = SmallLabel(self.video.date_published.strftime("%Y-%m-%d %H:%M:%S"), parent=self)
        self.eta_value = SmallLabel("No update", parent=self)
        self.speed_value = SmallLabel("No update:", parent=self)
        self.total_size_value = SmallLabel("No update:", parent=self)

        self.sane_layout.addWidget(self.title_bar, 0, 0, 1, 4)
        self.sane_layout.addWidget(self.thumbnail, 1, 0, 6, 1)
        self.sane_layout.addWidget(self.progress_bar, 7, 0, 1, 4)

        self.sane_layout.addWidget(self.status, 1, 1)
        self.sane_layout.addWidget(self.duration, 2, 1)
        self.sane_layout.addWidget(self.upload, 3, 1)
        self.sane_layout.addWidget(self.eta, 4, 1)
        self.sane_layout.addWidget(self.speed, 5, 1)
        self.sane_layout.addWidget(self.total_size, 6, 1)

        self.sane_layout.addWidget(self.status_value, 1, 2)
        self.sane_layout.addWidget(self.duration_value, 2, 2)
        self.sane_layout.addWidget(self.upload_value, 3, 2)
        self.sane_layout.addWidget(self.eta_value, 4, 2)
        self.sane_layout.addWidget(self.speed_value, 5, 2)
        self.sane_layout.addWidget(self.total_size_value, 6, 2)

        self.setLayout(self.sane_layout)

        self.download_progress_listener.updateProgress.connect(self.update_progress)
        self.download_progress_listener.finishedDownload.connect(self.finished_download)

        if db_download_tile:
            self.update_from_db_tile(db_download_tile)
        else:
            pass
        self.logger.debug("Init done")

    def update_from_db_tile(self, db_download_tile):
        self.finished = db_download_tile.finished
        self.started_date = db_download_tile.started_date
        self.finished_date = db_download_tile.finished_date
        self.video = db_download_tile.video
        self.video_downloaded = db_download_tile.video_downloaded
        self.total_bytes = db_download_tile.total_bytes
        self.last_event = db_download_tile.last_event

        if self.last_event:
            self.update_progress(self.last_event)

        if self.finished:
            self.status_value.setText("Finished")
        self.speed_value.setText("n/a")
        self.eta_value.setText("n/a")

    def finished_download(self):
        self.finished = True
        self.progress_bar.setValue(1000)
        self.progress_bar.setFormat("100.0%")
        self.status_value.setText("Finished")
        DownloadHandler.static_self.updateDownloadTile.emit(DDBDownloadTile(self))

    def update_progress(self, event):
        self.last_event = event
        # print(format(event))
        if "status" in event:
            if event["status"] == "finished":
                if not self.video_downloaded:
                    self.video_downloaded = True
                    self.status_value.setText("Finished downloading video")
                else:
                    self.status_value.setText("Finished")
            elif "downloading" == event["status"]:
                if self.video_downloaded:
                    self.status_value.setText("Downloading audio")
                else:
                    self.status_value.setText("Downloading video")
            else:
                self.status_value.setText(event["status"])
        if "_eta_str" in event:
            self.eta_value.setText(event["_eta_str"])
        if "_speed_str" in event:
            self.speed_value.setText(event["_speed_str"])
        if "_total_bytes_str" in event:
            self.total_size_value.setText(event["_total_bytes_str"])
        if "total_bytes" in event:
            if self.total_bytes == int(event["total_bytes"]):
                pass
            else:
                self.logger.debug("Downloading new item: {}".format(event))
                self.total_bytes = int(event["total_bytes"])
                # self.progress_bar.setMaximum(int(event["total_bytes"]))
        else:
            self.logger.warning("total_bytes not in: {}".format(event))
        if "downloaded_bytes" in event and self.total_bytes:
            self.progress_bar.setValue(int(int((event["downloaded_bytes"] / self.total_bytes) * 1000)))
        else:
            self.logger.warning("downloaded_bytes not in: {}".format(event))
        if "_percent_str" in event:
            self.progress_bar.setFormat(event["_percent_str"])

        DownloadHandler.static_self.updateDownloadTileEvent.emit(DDBDownloadTile(self))

    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
        menu = QMenu(self)

        is_paused = not self.download_progress_listener.threading_event.is_set()

        pause_action = None
        continue_dl_action = None

        if is_paused:
            continue_dl_action = menu.addAction("Continue download")
        else:
            pause_action = menu.addAction("Pause download")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == pause_action and pause_action:
            self.download_progress_listener.threading_event.clear()
            self.speed_value.setText("n/a")
            self.eta_value.setText("n/a")
        elif action == continue_dl_action and continue_dl_action:
            self.download_progress_listener.threading_event.set()
