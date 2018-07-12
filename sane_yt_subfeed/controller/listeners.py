# FIXME: imp*
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.video import Video


class GridViewListener(QObject):
    tileDownloaded = pyqtSignal(Video, int, int)
    tileDiscarded = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.tileDownloaded.connect(self.tile_downloaded)
        self.tileDiscarded.connect(self.tile_discarded)

    @pyqtSlot(VideoD, int, int)
    def tile_downloaded(self, video: Video, x, y):
        self.model.hide_grid_view_item(video, x, y)

    @pyqtSlot()
    def tile_discarded(self):
        print('hi')
        time.sleep(2)
        print('hello')

    def run(self):
        while True:
            time.sleep(2)



class DatabaseListener(QObject):
    databaseUpdated = pyqtSignal()

