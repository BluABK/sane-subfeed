from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QProgressBar, QWidget

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.download_view.download_thumbnail import DownloadThumbnailWidget


class DownloadTile(QWidget):
    def __init__(self, parent, download_progress_listener, *args, **kwargs):
        super(DownloadTile, self).__init__(parent, *args, **kwargs)
        self.sane_paret = parent
        self.download_progress_listener = download_progress_listener
        self.video = download_progress_listener.video
        self.total_bytes = None
        self.video_downloaded = False
        self.finished = False

        self.setFixedHeight(read_config('DownloadView', 'download_tile_height'))

        self.sane_layout = QGridLayout()
        self.sane_layout.setAlignment(Qt.AlignTop)

        self.title_bar = QLabel(self.video.title, parent=self)
        self.thumbnail = DownloadThumbnailWidget(self, self.video)
        self.progress_bar = QProgressBar(parent=self)

        self.status = QLabel("Status:", parent=self)
        self.duration = QLabel("Duration:", parent=self)
        self.upload = QLabel("Uploaded:", parent=self)
        self.eta = QLabel("ETA:", parent=self)
        self.speed = QLabel("Speed:", parent=self)
        self.total_size = QLabel("Total size:", parent=self)

        self.status_value = QLabel("No update", parent=self)
        self.duration_value = QLabel("Not Implemented", parent=self)
        self.upload_value = QLabel(self.video.date_published.strftime("%Y-%m-%d %H:%M:%S"), parent=self)
        self.eta_value = QLabel("No update", parent=self)
        self.speed_value = QLabel("No update:", parent=self)
        self.total_size_value = QLabel("No update:", parent=self)

        self.sane_layout.addWidget(self.title_bar, 0, 0, 1, 3)
        self.sane_layout.addWidget(self.thumbnail, 1, 0, 6, 1)
        self.sane_layout.addWidget(self.progress_bar, 7, 0, 1, 3)

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

    def update_progress(self, event):
        # print(format(event))
        if "status" in event:
            if event["status"] == "finished":
                if not self.video_downloaded:
                    self.video_downloaded = True
                    self.status_value.setText("Finished downloading video")
                else:
                    self.status_value.setText("Finished")
                    self.finished = True
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
            if self.total_bytes == event["total_bytes"]:
                pass
            else:
                self.total_bytes = event["total_bytes"]
                self.progress_bar.setMaximum(event["total_bytes"])
        if "downloaded_bytes" in event and self.total_bytes:
            self.progress_bar.setValue(event["downloaded_bytes"])
