# FIXME: imp*
import datetime
import os
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
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded, THUMBNAILS_PATH
from sane_yt_subfeed.youtube.update_videos import load_keys
from sane_yt_subfeed.youtube.youtube_dl_handler import YoutubeDownload
from sane_yt_subfeed.youtube.youtube_requests import get_remote_subscriptions_cached_oauth, list_uploaded_videos_videos

LISTENER_SIGNAL_NORMAL_REFRESH = 0
LISTENER_SIGNAL_DEEP_REFRESH = 1


class GridViewListener(QObject):
    tileDownloaded = pyqtSignal(VideoD)
    tileDiscarded = pyqtSignal(VideoD)
    tileWatched = pyqtSignal(VideoD)
    hiddenVideosChanged = pyqtSignal()
    downloadedVideosChanged = pyqtSignal()
    updateGridViewFromDb = pyqtSignal()
    updateFromDb = pyqtSignal()
    scrollReachedEndGrid = pyqtSignal()
    scrollReachedEndPlay = pyqtSignal()
    thumbnailDownload = pyqtSignal()

    # FIXME: move youtube-dl listener to its own listener?
    downloadFinished = pyqtSignal(VideoD)
    # FIXME: move to db listener
    downloadedVideosChangedinDB = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.logger = create_logger(__name__ + '.GridViewListener')

        self.tileDownloaded.connect(self.tile_downloaded)
        self.tileWatched.connect(self.tile_watched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.downloadFinished.connect(self.download_finished)
        self.downloadedVideosChangedinDB.connect(self.download_finished_in_db)
        self.updateGridViewFromDb.connect(self.update_grid_view_from_db)
        self.updateFromDb.connect(self.update_from_db)
        self.scrollReachedEndGrid.connect(self.scroll_reached_end_grid)
        self.scrollReachedEndPlay.connect(self.db_update_downloaded_videos)
        self.thumbnailDownload.connect(self.thumbnail_download)

    def thumbnail_download(self):
        self.model.update_thumbnails()
        self.logger.info("Updating thumbnails complete")
        self.downloadedVideosChanged.emit()
        self.hiddenVideosChanged.emit()

    def scroll_reached_end_grid(self):
        add_value = read_config("Model", "loaded_videos")
        self.model.videos_limit = self.model.videos_limit + add_value
        self.logger.info(
            "Scroll for Grid View reached 80%, updating videos limit to {}".format(self.model.videos_limit))
        self.model.db_update_videos()

    def db_update_downloaded_videos(self):
        add_value = read_config("Model", "loaded_videos")
        self.model.downloaded_videos_limit = self.model.downloaded_videos_limit + add_value
        self.logger.info(
            "Scroll for Play View reached 80%, updating videos limit to {}".format(self.model.downloaded_videos_limit))
        self.model.db_update_downloaded_videos()

    def update_from_db(self):
        self.model.db_update_videos()
        self.model.db_update_downloaded_videos()

    def update_grid_view_from_db(self):
        self.model.db_update_videos()

    @pyqtSlot(VideoD)
    def tile_downloaded(self, video: VideoD):
        self.model.hide_video_item(video)
        self.logger.info(
            "Video hidden from grid view(downloaded): {} - {} [{}]".format(video.channel_title, video.title,
                                                                           video.url_video))
        self.hiddenVideosChanged.emit()

        use_youtube_dl = read_config('Youtube-dl', 'use_youtube_dl')
        UpdateVideo(video, update_existing=True).start()
        if use_youtube_dl:
            YoutubeDownload(video, finished_listener=self.downloadFinished).start()

    @pyqtSlot(VideoD)
    def download_finished(self, video: VideoD):
        UpdateVideo(video, update_existing=True, finished_listeners=[self.downloadedVideosChangedinDB]).start()

    def download_finished_in_db(self):
        self.model.db_update_downloaded_videos()

    @pyqtSlot(VideoD)
    def tile_watched(self, video: Video):
        self.model.hide_downloaded_video_item(video)
        self.downloadedVideosChanged.emit()
        UpdateVideo(video, update_existing=True).start()

    @pyqtSlot(VideoD)
    def tile_discarded(self, video: Video):
        self.model.hide_video_item(video)
        self.logger.info("Video hidden from grid view(Discarded): {} - {} [{}]".format(video.channel_title, video.title,
                                                                                       video.url_video))
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
        self.logger = create_logger(__name__ + '.MainWindowListener')

    def run(self):
        while True:
            time.sleep(2)

    @pyqtSlot(int)
    def refresh_videos(self, refresh_type):
        """
        Fetches new videos and reloads the subscription feed
        :return:
        """
        self.logger.info("Reloading subfeed")
        hide_downloaded = read_config('Gui', 'hide_downloaded')
        if hide_downloaded:
            self.model.remote_update_videos(refresh_type=refresh_type)
            self.model.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.model.remote_update_videos(refresh_type=refresh_type)
            self.logger.error('NOT IMPLEMENTED: disabled hide_downloaded')

    @pyqtSlot()
    def refresh_subs(self):
        """
        Fetches a new list of subscriptions from YouTube API via OAuth
        :return:
        """
        self.logger.info("Reloading subscriptions list")
        get_remote_subscriptions_cached_oauth()

    @pyqtSlot()
    def test_channels(self):
        """
        Runs the test channels test
        :return:
        """
        self.logger.info("Running test: channels test")
        main.run_channels_test()


class DatabaseListener(QObject):
    databaseUpdated = pyqtSignal()
    refreshVideos = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideos.connect(self.refresh_videos)
        self.logger = create_logger(__name__ + '.DatabaseListener')

    def run(self):
        while True:
            time.sleep(2)

    @pyqtSlot()
    def refresh_videos(self):
        self.logger.info('Reloading videos')


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
        self.logger = create_logger(__name__ + '.ProgressBar')

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
        self.logger = create_logger(__name__ + '.YtDirListener')
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
            if not vid.downloaded:
                vid.vid_path = vid_path
                vid.date_downloaded = datetime.datetime.utcnow()
                vid.downloaded = True

                thumb_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(vid.video_id))
                downloaded_thumbnail = os.path.isfile(thumb_path)
                if downloaded_thumbnail and (not vid.thumbnail_path):
                    vid.thumbnail_path = thumb_path
                    self.logger.warning(
                        "Thumbnail downloaded, but path didn't exist in db, for video: {}".format(vid.__dict__))
                elif (not vid.thumbnail_path) or (not downloaded_thumbnail):
                    if not downloaded_thumbnail:
                        self.warning.info("Thumbnail path in db, but not on disk, for video: {}".format(vid.__dict__))
                    self.logger.info("Downloading thumbnail for: {}".format(vid.__dict__))
                    download_thumbnails_threaded(vid)

                self.logger.info("Updating existing record in db")
                db_session.commit()
                self.model.db_update_videos()
                self.model.db_update_downloaded_videos()
            else:
                self.logger.info("File already downloaded by this system")
            db_session.remove()

        else:
            db_session.remove()
            youtube_keys = load_keys(1)
            self.logger.info("Grabbing new video information from youtube")
            response_videos = list_uploaded_videos_videos(youtube_keys[0], [vid_id], 1)
            if len(response_videos) > 0:
                video = response_videos[0]
                video.vid_path = vid_path
                video.downloaded = True
                video.date_downloaded = datetime.datetime.utcnow()
                self.logger.info("Downloading thumbnail")
                download_thumbnails_threaded([video])
                self.logger.info("Adding new file to db")
                UpdateVideo(video,
                            finished_listeners=[self.model.grid_view_listener.downloadedVideosChangedinDB]).start()
            else:
                self.logger.warning("Video with id {}, not found on youtube servers".format(vid_id))

    @pyqtSlot()
    def manual_check(self):
        youtube_folder = read_config("Play", "yt_file_path", literal_eval=False)
        CheckYoutubeFolderForNew(youtube_folder,
                                 db_listeners=[self.model.grid_view_listener.downloadedVideosChangedinDB,
                                               self.model.grid_view_listener.updateGridViewFromDb]).start()
