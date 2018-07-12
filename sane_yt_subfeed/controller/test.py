import time

from PyQt5.QtCore import QObject, pyqtSignal


class MainWindowListener(QObject):
    refreshVideosfwheiuf = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideosfwheiuf.connect(self.refresh_videoswesfsef)

    def run(self):
        while True:
            time.sleep(2)


    def refresh_videoswesfsef(self):
        print('refresh')
