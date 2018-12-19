from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSizePolicy

from sane_yt_subfeed.gui.views.download_view.buttons.clear_finished import ClearFinishedDownloads


class ButtonsTile(QWidget):

    def __init__(self, parent):
        super(ButtonsTile, self).__init__(parent=parent)
        self.sane_parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.sane_layout = QHBoxLayout()
        self.sane_layout.setAlignment(Qt.AlignTop)

        self.clear_button = ClearFinishedDownloads(self, self.sane_parent)

        self.sane_layout.addWidget(self.clear_button)

        self.setLayout(self.sane_layout)
