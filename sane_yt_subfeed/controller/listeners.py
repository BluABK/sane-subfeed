# FIXME: imp*
import datetime
import time

from PyQt5.QtCore import *

from sane_yt_subfeed import main

from watchdog.observers import Observer
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.dir_handler import VidEventHandler, manual_youtube_folder_check, \
    CheckYoutubeFolderForNew
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo, UpdateVideosThread
from sane_yt_subfeed.log_handler import logger
from sane_yt_subfeed.youtube.youtube_dl_handler import YoutubeDownload
from sane_yt_subfeed.youtube.youtube_requests import get_remote_subscriptions_cached_oauth

LISTENER_SIGNAL_NORMAL_REFRESH = 0
LISTENER_SIGNAL_DEEP_REFRESH = 1


class GridViewListener(QObject):
    tileDownloaded = pyqtSignal(VideoD, int)
    tileDiscarded = pyqtSignal(VideoD, int)
    tileWatched = pyqtSignal(VideoD, int)
    hiddenVideosChanged = pyqtSignal()
    downloadedVideosChanged = pyqtSignal()
    # FIXME: move youtube-dl listener to its own listener?
    downloadFinished = pyqtSignal(VideoD)
    # FIXME: move to db listener
    downloadedVideosChangedinDB = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.tileDownloaded.connect(self.tile_downloaded)
        self.tileWatched.connect(self.tile_watched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.downloadFinished.connect(self.download_finished)
        self.downloadedVideosChangedinDB.connect(self.download_finished_in_db)

    @pyqtSlot(VideoD, int)
    def tile_downloaded(self, video: VideoD, index):
        self.model.hide_video_item(index)
        self.hiddenVideosChanged.emit()

        use_youtube_dl = read_config('Youtube-dl', 'use_youtube_dl')
        UpdateVideo(video, update_existing=True).start()
        if use_youtube_dl:
            YoutubeDownload(video, finished_listener=self.downloadFinished).start()

    @pyqtSlot(VideoD)
    def download_finished(self, video: VideoD):
        UpdateVideo(video, update_existing=True, finished_listener=self.downloadedVideosChangedinDB).start()

    def download_finished_in_db(self):
        self.model.db_update_downloaded_videos()

    @pyqtSlot(VideoD, int)
    def tile_watched(self, video: Video, index):
        self.model.hide_downloaded_video_item(index)
        self.downloadedVideosChanged.emit()
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


class YtDirListener(QObject):
    newFile = pyqtSignal(str, str)
    manualCheck = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.newFile.connect(self.new_file)
        self.manualCheck.connect(self.manual_check)

        disable_dir_observer = read_config('Play', 'disable_dir_listener')
        if not disable_dir_observer:
            path = read_config('Play', 'yt_file_path', literal_eval=False)
            event_handler = VidEventHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, path)
            self.observer.start()

    def run(self):
        while True:
            time.sleep(2)

    @pyqtSlot(str, str)
    def new_file(self, vid_id, vid_path):

        vid = db_session.query(Video).get(vid_id)
        if vid:
            vid.vid_path = vid_path
            vid.date_downloaded = datetime.datetime.utcnow()
            vid.downloaded = True

            db_session.commit()
            db_session.remove()

            self.model.db_update_videos()
            self.model.db_update_downloaded_videos()

    @pyqtSlot()
    def manual_check(self):
        youtube_folder = read_config("Play", "yt_file_path", literal_eval=False)
        CheckYoutubeFolderForNew(youtube_folder,
                                 db_listener=self.model.grid_view_listener.downloadedVideosChangedinDB).start()
