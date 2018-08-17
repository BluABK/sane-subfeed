from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QProgressBar, QSizePolicy


class DownloadProgressBar(QProgressBar):
    def __init__(self, parent):
        super(DownloadProgressBar, self).__init__(parent=parent)
        self.sane_parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMaximum(1000)
        # self.setTextVisible(True)
        self.setAlignment(Qt.AlignCenter)

