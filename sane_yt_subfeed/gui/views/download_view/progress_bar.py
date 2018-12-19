from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QProgressBar, QSizePolicy


class DownloadProgressBar(QProgressBar):
    def __init__(self, parent):
        super(DownloadProgressBar, self).__init__(parent=parent)
        self.sane_parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMaximum(1000)
        # self.setTextVisible(True)
        self.setAlignment(Qt.AlignCenter)
        self.default_palette = QPalette(self.palette())

    def set_color(self, color):
        palette = QPalette(self.palette())
        palette.setColor(QPalette.Highlight, color)
        self.setPalette(palette)

    def reset_palette(self):
        self.setPalette(self.default_palette)

    def pause(self):
        self.set_color(Qt.darkYellow)

    def resume(self):
        self.reset_palette()

    def finish(self):
        self.set_color(Qt.darkGreen)

    def fail(self):
        self.set_color(Qt.darkRed)
