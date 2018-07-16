# FIXME: imp*
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.read_operations import refresh_and_get_newest_videos
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.log_handler import logger


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


class MainWindowListener(QObject):
    refreshVideos = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideos.connect(self.refresh_videos)

    def run(self):
        while True:
            time.sleep(2)

    @pyqtSlot()
    def refresh_videos(self):
        logger.info("Reloading subfeed")
        hide_downloaded = read_config('Gui', 'hide_downloaded')
        if hide_downloaded:
            self.model.filtered_videos = refresh_and_get_newest_videos(self.model.videos_limit, hide_downloaded)
            self.model.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.model.videos = refresh_and_get_newest_videos(self.model.videos_limit, hide_downloaded)


class DatabaseListener(QObject):
    databaseUpdated = pyqtSignal()
    refreshVideos = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideos.connect(self.refresh_videos)

    def run(self):
        while True:
            time.sleep(2)

    @pyqtSlot()
    def refresh_videos(self):
        print('refresh')
