from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from sane_yt_subfeed.gui.views.download_view.buttons.clear_finished import ClearFinishedDownloads


class ButtonsTile(QWidget):

    def __init__(self, parent):
        super(ButtonsTile, self).__init__(parent=parent)
        self.sane_parent = parent

        self.sane_layout = QHBoxLayout()

        self.clear_button = ClearFinishedDownloads(self, self.sane_parent)

        self.sane_layout.addWidget(self.clear_button)

        self.setLayout(self.sane_layout)