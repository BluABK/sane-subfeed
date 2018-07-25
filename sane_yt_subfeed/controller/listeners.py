# FIXME: imp*
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from sane_yt_subfeed import main
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.log_handler import logger
from sane_yt_subfeed.youtube.youtube_requests import get_remote_subscriptions_cached_oauth

LISTENER_SIGNAL_NORMAL_REFRESH = 0
LISTENER_SIGNAL_DEEP_REFRESH = 1

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
    testChannels = pyqtSignal()
    refreshVideos = pyqtSignal(int)
    refreshSubs = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideos.connect(self.refresh_videos)
        self.refreshSubs.connect(self.refresh_subs)
        self.testChannels.connect(self.test_channels)

    def run(self):
        while True:
            time.sleep(2)
            logger.debug('MainWindowListener: is alive')
        # noinspection PyUnreachableCode
        logger.error('MainWindowListener finished')

    @pyqtSlot(int)
    def refresh_videos(self, refresh_type):
        """
        Fetches new videos and reloads the subscription feed
        :return:
        """
        logger.info("Reloading subfeed")
        hide_downloaded = read_config('Gui', 'hide_downloaded')
        if hide_downloaded:
            self.model.remote_update_videos(refresh_type=refresh_type)
            self.model.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.model.remote_update_videos(refresh_type=refresh_type)
            logger.debug('MainWindowListener: not implemented disabled hide_downloaded')

    @pyqtSlot()
    def refresh_subs(self):
        """
        Fetches a new list of subscriptions from YouTube API via OAuth
        :return:
        """
        logger.info("Reloading subscriptions list")
        get_remote_subscriptions_cached_oauth()

    @pyqtSlot()
    def test_channels(self):
        """
        Runs the test channels test
        :return:
        """
        main.run_channels_test()


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


class ProgressBar(QObject):
    setMaximum = pyqtSignal(int)
    setProgress = pyqtSignal(int)
    updateProgress = pyqtSignal()
    setText = pyqtSignal(str)
    resetBar = pyqtSignal()
    progress_bar = None

    def __init__(self, model, progress_bar):
        super().__init__()
        self.model = model
        self.progress_bar = progress_bar
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.setMaximum.connect(self.set_maximum)
        self.setProgress.connect(self.set_progress)
        self.updateProgress.connect(self.update_progress)
        self.setText.connect(self.set_text)
        self.resetBar.connect(self.reset_bar)

    def run(self):
        while True:
            time.sleep(2)

    def set_maximum(self, max):
        self.progress_bar.setMaximum(max)

    def set_progress(self, progress):
        self.progress_bar.setValue(progress)
        self.progress_bar.update()

    def update_progress(self):
        value = self.progress_bar.value()
        self.progress_bar.setValue(value + 1)
        self.progress_bar.update()

    def set_text(self, text):
        self.progress_bar.setFormat(text)
        # self.progress_bar.text = text
        self.progress_bar.update()

    def reset_bar(self):
        self.progress_bar.reset()
        self.progress_bar.update()
