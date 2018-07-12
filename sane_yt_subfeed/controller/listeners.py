# FIXME: imp*
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo


class GridViewListener(QObject):
    tileDownloaded = pyqtSignal(VideoD, int)
    tileDiscarded = pyqtSignal(VideoD, int)
    hiddenVideosChanged = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.tileDownloaded.connect(self.tile_downloaded)
        self.tileDiscarded.connect(self.tile_discarded)

    @pyqtSlot(VideoD, int)
    def tile_downloaded(self, video: Video, index):
        self.model.hide_video_item(index)
        self.hiddenVideosChanged.emit()
        UpdateVideo(video, update_existing=True).start()

    @pyqtSlot(VideoD, int)
    def tile_discarded(self, video: Video, index):
        self.model.hide_video_item(index)
        self.hiddenVideosChanged.emit()
        UpdateVideo(video, update_existing=True).start()

    def run(self):
        while True:
            time.sleep(2)



class DatabaseListener(QObject):
    databaseUpdated = pyqtSignal()

