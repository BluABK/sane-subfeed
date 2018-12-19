from PyQt5.QtWidgets import QPushButton


class ClearFinishedDownloads(QPushButton):

    def __init__(self, parent, download_view, *__args):
        super(ClearFinishedDownloads, self).__init__(*__args, parent=parent)
        self.setText("Clear finished downloads")
        self.sane_parent = parent
        self.download_view = download_view

        self.clicked.connect(download_view.clear_finished_downloads)
