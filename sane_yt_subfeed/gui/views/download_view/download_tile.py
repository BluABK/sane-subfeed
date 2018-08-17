from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QProgressBar, QWidget


class DownloadTile(QWidget):
    def __init__(self, parent, download_progress_listener, *args, **kwargs):
        super(DownloadTile, self).__init__(parent, *args, **kwargs)
        self.sane_paret = parent
        self.download_progress_listener = download_progress_listener
        self.video = download_progress_listener.video

        self.sane_layout = QGridLayout()
        self.sane_layout.setAlignment(Qt.AlignTop)

        self.title_bar = QLabel("Title:", parent=self)
        self.thumbnail = QLabel("Img", parent=self)
        self.progress_bar = QProgressBar(parent=self)

        self.status = QLabel("Status:", parent=self)
        self.duration = QLabel("Duration:", parent=self)
        self.upload = QLabel("Uploaded:", parent=self)
        self.eta = QLabel("ETA:", parent=self)

        self.status_value = QLabel("Not Implemented", parent=self)
        self.duration_value = QLabel("Not Implemented", parent=self)
        self.upload_value = QLabel("Not Implemented", parent=self)
        self.eta_value = QLabel("Not Implemented", parent=self)

        self.sane_layout.addWidget(self.title_bar, 0, 0, 1, 3)
        self.sane_layout.addWidget(self.thumbnail, 1, 0, 4, 1)
        self.sane_layout.addWidget(self.progress_bar, 5, 0, 1, 3)

        self.sane_layout.addWidget(self.status, 1, 1)
        self.sane_layout.addWidget(self.duration, 2, 1)
        self.sane_layout.addWidget(self.upload, 3, 1)
        self.sane_layout.addWidget(self.eta, 4, 1)

        self.sane_layout.addWidget(self.status_value, 1, 2)
        self.sane_layout.addWidget(self.duration_value, 2, 2)
        self.sane_layout.addWidget(self.upload_value, 3, 2)
        self.sane_layout.addWidget(self.eta_value, 4, 2)

        self.setLayout(self.sane_layout)
