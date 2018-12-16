from PyQt5 import sip
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
        self.root = parent.root
        self.parent = parent

        if download_progress_listener:
            self.download_progress_listener = download_progress_listener
            self.video = download_progress_listener.video
            self.download_progress_listener.updateProgress.connect(self.update_progress)
            self.download_progress_listener.finishedDownload.connect(self.finished_download)
        elif db_download_tile:
            self.download_progress_listener = None
            self.video = db_download_tile.video

        self.total_bytes = None
        self.total_bytes_video = None
        self.total_bytes_audio = None
        self.video_downloaded = False
        self.finished = False
        self.paused = False
        self.failed = False  # FIXME: Implement handling of failed downloads
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

        self.percentage_downloaded = 0
        # self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.status = SmallLabel("Status:", parent=self)
        self.duration = SmallLabel("Duration:", parent=self)
        self.upload = SmallLabel("Uploaded:", parent=self)
        self.eta = SmallLabel("ETA:", parent=self)
        self.speed = SmallLabel("Speed:", parent=self)
        self.total_size = SmallLabel("Total size:", parent=self)

        self.status_value = SmallLabel("No update", parent=self)
        self.duration_value = SmallLabel(format(self.video.duration), parent=self)
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
            self.progress_bar.finish()
        if self.paused:
            self.status_value.setText("Paused")
            self.progress_bar.pause()
        if self.failed:
            self.status_value.setText("FAILED")
            self.progress_bar.fail()
        self.speed_value.setText("N/A")
        self.eta_value.setText("N/A")

    def paused_download(self):
        self.logger.debug5("Paused download")
        self.paused = True
        self.download_progress_listener.threading_event.clear()
        self.progress_bar.pause()

    def resumed_download(self):
        self.logger.debug5("Resumed download")
        self.paused = False
        self.download_progress_listener.threading_event.set()
        self.progress_bar.resume()

    def failed_download(self):
        self.logger.debug5("Failed download")
        self.failed = True
        self.download_progress_listener.threading_event.clear()
        self.progress_bar.fail()
        DownloadHandler.static_self.updateDownloadTile.emit(DDBDownloadTile(self))

    def determine_si_unit(self, byte_value):
        """
        Walks a size of bytes through SI Units until it finds the appropriate one to use.
        :param byte_value:
        :return:
        """
        si_units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
        for unit in si_units:
            if byte_value < 1024:
                # Cannot switch from manual field specification to automatic field numbering, thus separate variable.
                byte_value_formatted = "{0:.2f}".format(byte_value)
                return "{}{}".format(byte_value_formatted, unit)
            byte_value = byte_value/1024

        # You should never reach this point
        self.logger.error("BUG in determine_si_unit: Bytes received larger than YiB unit!!!")
        return "Uh oh... (see log)"

    def finished_download(self):
        self.finished = True
        self.progress_bar.setValue(1000)
        self.progress_bar.setFormat("100.0%")
        self.status_value.setText("Finished")
        try:
            combined_size = self.total_bytes_video + self.total_bytes_audio
            self.total_size_value.setText(self.determine_si_unit(combined_size))
        except TypeError as te_exc:
            self.logger.error("A TypeError exception occurred while combining video+audio track sizes", exc_info=te_exc)
            self.total_size_value.setText("BUG: GitHub Issue #28")
        self.progress_bar.finish()
        DownloadHandler.static_self.updateDownloadTile.emit(DDBDownloadTile(self))

    def delete_incomplete_entry(self):
        """
        Deletes an incomplete entry from the parent (DownloadView).
        :return:
        """
        message = "Are you sure you want to remove '{}' from Downloads?".format(self.video.title)
        actions = self.parent.clear_download_forced
        # Prompt user for a confirmation dialog which applies actions to caller if confirmed.
        self.root.confirmation_dialog(message, actions, caller=self)

    def update_progress(self, event):
        self.last_event = event
        # print(format(event))
        if "status" in event:
            if event["status"] == "finished":
                if not self.video_downloaded:
                    self.video_downloaded = True
                    self.status_value.setText("Finished downloading video")
                else:
                    # It's not really finished until it calls finished_download()
                    self.status_value.setText("Postprocessing...")
            elif "downloading" == event["status"]:
                if self.paused:
                    self.status_value.setText("Download paused")
                elif self.failed:
                    self.status_value.setText("Download FAILED!")
                else:
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
        if "total_bytes" in event or "total_bytes_estimate" in event:
            if "total_bytes" not in event:
                event["total_bytes"] = event["total_bytes_estimate"]
            if self.total_bytes == int(event["total_bytes"]):
                pass
            else:
                self.logger.debug("Downloading new item: {}".format(event))
                self.total_bytes = int(event["total_bytes"])
                # Store total bytes for video and audio track in a safe place
                if not self.video_downloaded:
                    self.total_bytes_video = self.total_bytes
                self.total_bytes_audio = self.total_bytes
                # self.progress_bar.setMaximum(int(event["total_bytes"]))
        else:
            self.logger.warning("total_bytes not in: {}".format(event))
        if "downloaded_bytes" in event and self.total_bytes:
            self.progress_bar.setValue(int(int((event["downloaded_bytes"] / self.total_bytes) * 1000)))
            percentage_downloaded = int((event["downloaded_bytes"] / self.total_bytes) * 100)
            if percentage_downloaded > self.percentage_downloaded:
                self.percentage_downloaded = percentage_downloaded
                DownloadHandler.static_self.updateDownloadTileEvent.emit(DDBDownloadTile(self))
        else:
            if "downloaded_bytes" not in event:
                self.logger.warning("downloaded_bytes not in: {}".format(event))
        if "_percent_str" in event:
            self.progress_bar.setFormat(event["_percent_str"])

    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
        if self.download_progress_listener:
            menu = QMenu(self)

            is_paused = not self.download_progress_listener.threading_event.is_set()

            pause_action = None
            continue_dl_action = None

            if is_paused:
                continue_dl_action = menu.addAction("Continue download")
            else:
                pause_action = menu.addAction("Pause download")
            if not self.finished:
                delete_incomplete_entry = menu.addAction("Delete incomplete entry")

            action = menu.exec_(self.mapToGlobal(event.pos()))

            if not self.finished:
                if action == pause_action and pause_action:
                    self.paused_download()
                elif action == continue_dl_action and continue_dl_action:
                    self.resumed_download()
                elif action == delete_incomplete_entry:
                    self.delete_incomplete_entry()

