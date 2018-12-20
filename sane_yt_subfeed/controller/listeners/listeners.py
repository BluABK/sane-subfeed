# FIXME: imp*
import gc
import time

import datetime
import os
import types
from PyQt5.QtCore import *
from functools import wraps
from watchdog.observers import Observer

from sane_yt_subfeed import main
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.dir_handler import VidEventHandler, CheckYoutubeFolderForNew
from sane_yt_subfeed.controller.listeners import static_listeners
from sane_yt_subfeed.controller.listeners.download_handler import DownloadHandler
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded, THUMBNAILS_PATH
from sane_yt_subfeed.youtube.update_videos import load_keys
from sane_yt_subfeed.youtube.youtube_requests import get_remote_subscriptions_cached_oauth, list_uploaded_videos_videos, \
    add_subscription

LISTENER_SIGNAL_NORMAL_REFRESH = 0
LISTENER_SIGNAL_DEEP_REFRESH = 1

logger = create_logger(__name__ + '.listeners')


class GridViewListener(QObject):
    static_self = None

    # Subfeed
    hiddenVideosChanged = pyqtSignal()
    hiddenVideosUpdated = pyqtSignal()
    # Playback
    playbackVideosChanged = pyqtSignal()
    playbackVideosUpdated = pyqtSignal()
    decreaseWatchPrio = pyqtSignal(VideoD)
    increaseWatchPrio = pyqtSignal(VideoD)
    # GridView / Shared
    tileDownloaded = pyqtSignal(VideoD)
    tileDiscarded = pyqtSignal(VideoD)
    tileUndiscarded = pyqtSignal(VideoD)
    tileWatched = pyqtSignal(VideoD)
    tileUnwatched = pyqtSignal(VideoD)
    updateGridViewFromDb = pyqtSignal()
    updateFromDb = pyqtSignal()
    scrollReachedEndGrid = pyqtSignal()
    scrollReachedEndPlay = pyqtSignal()
    thumbnailDownload = pyqtSignal()
    redrawVideos = pyqtSignal(list)

    # FIXME: move youtube-dl listener to its own listener?
    downloadFinished = pyqtSignal(VideoD)
    # FIXME: move to db listener
    downloadedVideosChangedinDB = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.logger = create_logger(__name__ + '.GridViewListener')
        GridViewListener.static_self = self
        static_listeners.STATIC_GRID_VIEW_LISTENER = self

        self.tileDownloaded.connect(self.tile_downloaded)
        self.tileWatched.connect(self.tile_watched)
        self.tileUnwatched.connect(self.tile_unwatched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.tileUndiscarded.connect(self.tile_undiscarded)
        self.downloadFinished.connect(self.download_finished)
        self.downloadedVideosChangedinDB.connect(self.download_finished_in_db)
        self.updateGridViewFromDb.connect(self.update_grid_view_from_db)
        self.updateFromDb.connect(self.update_from_db)
        self.scrollReachedEndGrid.connect(self.scroll_reached_end_grid)
        self.scrollReachedEndPlay.connect(self.scroll_reached_end_play)
        self.thumbnailDownload.connect(self.thumbnail_download)
        self.decreaseWatchPrio.connect(self.decrease_watch_prio)
        self.increaseWatchPrio.connect(self.increase_watch_prio)

    @pyqtSlot(VideoD)
    def decrease_watch_prio(self, video):
        """
        Decreases the priority of a video, which will put it further down the list in a sort.
        :param video:
        :return:
        """
        self.logger.info("Decreasing watch prio for: {}".format(video.__dict__))
        video.watch_prio += 1
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True, finished_listeners=[self.downloadedVideosChangedinDB]).start()

    @pyqtSlot(VideoD)
    def increase_watch_prio(self, video):
        """
        Increases the priority of a video, which will put it further up the list in a sort.
        :param video:
        :return:
        """
        self.logger.info("Increasing watch prio for: {}".format(video.__dict__))
        video.watch_prio -= 1
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True, finished_listeners=[self.downloadedVideosChangedinDB]).start()

    def thumbnail_download(self):
        """
        Updates downloaded thumbnails.
        :return:
        """
        self.model.update_thumbnails()
        self.logger.debug("Updating thumbnails complete")
        self.playbackVideosUpdated.emit()
        self.hiddenVideosUpdated.emit()

    def scroll_reached_end_grid(self):
        """
        Reaction to SubfeedGridView scrollbar reaching the end.

        If there are more videos in the list, load a videos_limit amount of them.
        :return:
        """
        add_value = read_config("Model", "loaded_videos")
        self.model.videos_limit = self.model.videos_limit + add_value
        self.logger.info(
            "Scroll for Sub Feed reached end, updating videos limit to {}".format(self.model.videos_limit))
        self.model.update_subfeed_videos_from_db()

    def scroll_reached_end_play(self):
        """
        Reaction to PlaybackGridView scrollbar reaching the end.

        If there are more videos in the list, load a videos_limit amount of them.
        :return:
        """
        add_value = read_config("Model", "loaded_videos")
        self.model.playview_videos_limit = self.model.playview_videos_limit + add_value
        self.logger.info(
            "Scroll for Play View reached end, updating videos limit to {}".format(self.model.playview_videos_limit))
        self.model.update_playback_videos_from_db()

    def update_from_db(self):
        """
        Update Subfeed and Playback Views from DB.
        :return:
        """
        self.model.update_subfeed_videos_from_db()
        self.model.update_playback_videos_from_db()

    def update_grid_view_from_db(self):
        """
        Update only Subfeed View from DB.
        :return:
        """
        self.model.update_subfeed_videos_from_db()

    @pyqtSlot(VideoD)
    def tile_downloaded(self, video: VideoD):
        """
        Action to take if tile has been flagged as downloaded.

        Called by Views: Subfeed
        :param video:
        :return:
        """
        self.logger.info(
            "Hide video(Downloading): {} - {} [{}]".format(video.channel_title, video.title,
                                                           video.url_video))
        video.downloaded = True
        self.model.hide_video_item(video)
        self.hiddenVideosChanged.emit()
        DownloadHandler.download_video(video,
                                       youtube_dl_finished_listener=[self.downloadFinished],
                                       db_update_listeners=[self.downloadedVideosChangedinDB])

    @pyqtSlot(VideoD)
    def download_finished(self, video: VideoD):
        """
        Action to take if download has finished.
        :param video:
        :return:
        """
        self.redrawVideos.emit([video])
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True, finished_listeners=[self.downloadedVideosChangedinDB]).start()

    def download_finished_in_db(self):
        """
        Action to take if tile has been flagged as downloaded (DB version).
        :return:
        """
        self.model.update_playback_videos_from_db()

    def playback_tile_update_and_redraw(self, video: Video):
        """
        Common operations for Playback tiles.
        :param video:
        :return:
        """
        # Update Playback View
        self.playbackVideosChanged.emit()
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True).start()
        # Update PlaybackGridView from database.
        self.model.update_playback_videos_from_db()
        # Redraw the video
        self.redrawVideos.emit([video])

    def subfeed_tile_update_and_redraw(self, video: Video):
        """
        Common operations for Subfeed tiles.
        :param video:
        :return:
        """
        # Update Subfeed View
        self.hiddenVideosChanged.emit()
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True).start()
        # Update SubfeedGridView from database.
        self.model.update_subfeed_videos_from_db()
        # Redraw the video
        self.redrawVideos.emit([video])

    @pyqtSlot(VideoD)
    def tile_watched(self, video: Video):
        """
        Action to take if tile has been flagged as watched.

        Called by Views: Playback
        :param video:
        :return:
        """
        self.logger.info("Mark watched: {} - {}".format(video.title, video.__dict__))
        video.watched = True
        self.model.hide_video_item(video)
        self.playback_tile_update_and_redraw(video)

    @pyqtSlot(VideoD)
    def tile_unwatched(self, video: Video):
        """
        Action to take if tile has been un-flagged as watched.

        Called by Views: Playback
        :param video:
        :return:
        """
        self.logger.info("Mark unwatched: {} - {}".format(video.title, video.__dict__))
        video.watched = False
        self.model.unhide_video_item(video)
        self.playback_tile_update_and_redraw(video)

    @pyqtSlot(VideoD)
    def tile_discarded(self, video: Video):
        """
        Action to take if tile has been flagged as dismissed.

        Called by Views: Subfeed and Playback
        :param video:
        :return:
        """
        self.logger.info("Hide video (Discarded): {} - {} [{}]".format(video.channel_title, video.title,
                                                                       video.url_video))
        video.discarded = True
        self.model.hide_video_item(video)
        self.playback_tile_update_and_redraw(video)
        self.subfeed_tile_update_and_redraw(video)

    @pyqtSlot(VideoD)
    def tile_undiscarded(self, video: Video):
        """
        Action to take if tile has been un-flagged as dismissed.

        Called by Views: Subfeed and Playback
        :param video:
        :return:
        """
        self.logger.info("Un-hide video (Un-discarded): {} - {} [{}]".format(video.channel_title,
                                                                             video.title,
                                                                             video.url_video))
        video.discarded = False
        self.model.unhide_video_item(video)
        self.playback_tile_update_and_redraw(video)
        self.subfeed_tile_update_and_redraw(video)

    def run(self):
        while True:
            time.sleep(2)


def exception_pyqt_slot(*args):
    """
    Create a decorator that wraps PyQt' new signal/slot decorators and provides exception handling for all slots.
    :param args:
    :return:
    """
    if len(args) == 0 or isinstance(args[0], types.FunctionType):
        args = []

    @pyqtSlot(*args)
    def slotdecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args)
            except Exception as e:
                logger.critical("Uncaught Exception in slot", exc_info=e)
                # traceback.print_exc()

        return wrapper

    return slotdecorator


class MainWindowListener(QObject):
    testChannels = pyqtSignal()
    refreshVideos = pyqtSignal(int)
    refreshSubs = pyqtSignal()
    getSingleVideo = pyqtSignal(str)
    addYouTubeChannelSubscriptionById = pyqtSignal(str)
    addYouTubeChannelSubscriptionByUsername = pyqtSignal(str)
    raiseGenericException = pyqtSignal()
    raiseException = pyqtSignal(Exception)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideos.connect(self.refresh_videos)
        self.refreshSubs.connect(self.refresh_subs)
        self.testChannels.connect(self.test_channels)
        self.getSingleVideo.connect(self.get_single_video)
        self.addYouTubeChannelSubscriptionById.connect(self.add_youtube_channel_subscription_by_id)
        self.addYouTubeChannelSubscriptionByUsername.connect(self.add_youtube_channel_subscription_by_username)
        self.raiseGenericException.connect(self.raise_generic_exception)
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
            self.model.update_subfeed_videos_from_remote(refresh_type=refresh_type)
            # self.model.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.model.update_subfeed_videos_from_remote(refresh_type=refresh_type)
            self.logger.error('NOT IMPLEMENTED: disabled hide_downloaded')

        # Attempt to force garbage collection to close unnecessary sockets
        gc.collect()

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

    @pyqtSlot(str)
    def get_single_video(self, video_url):
        """
        Fetches a specified video based on url
        :return:
        """
        self.logger.info("Fetching video: {}".format(video_url))
        video_id = video_url.split('&')[0].split('v=')[-1]  # FIXME: Make a proper input sanitizer that handles YT IDs
        self.logger.debug("{} --> ID: {}".format(video_url, video_id))
        video_d = list_uploaded_videos_videos(load_keys(1)[0], [video_id], 50)[0]
        download_thumbnails_threaded([video_d])
        DownloadHandler.download_video(video_d,
                                       youtube_dl_finished_listener=[GridViewListener.static_self.downloadFinished],
                                       db_update_listeners=[GridViewListener.static_self.downloadedVideosChangedinDB])

    @pyqtSlot(str)
    def add_youtube_channel_subscription_by_id(self, channel_id):
        """
        Subscribes to a channel based on channel ID
        :return:
        """
        self.logger.info("Adding subscription to channel: '{}'".format(channel_id))
        add_subscription(load_keys(1)[0], channel_id)

    @pyqtSlot(str)
    def add_youtube_channel_subscription_by_username(self, username):
        """
        Subscribes to a channel based on username
        :return:
        """
        self.logger.info("Adding subscription to channel: '{}'".format(username))
        add_subscription(load_keys(1)[0], username, by_username=True)

    def raise_generic_exception(self):
        """
        Raises a generic Exception. (Used for debug)
        :return:
        """
        raise Exception("Generic Exception (backend)")


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
                        self.logger.warning("Thumbnail path in db, but not on disk, for video: {}".format(vid.__dict__))
                    self.logger.info("Downloading thumbnail for: {}".format(vid.__dict__))
                    download_thumbnails_threaded([vid])

                self.logger.info("Updating existing record in db: {} - {}".format(vid.title, vid.__dict__))
                db_session.commit()
                self.model.update_subfeed_videos_from_db()
                self.model.update_playback_videos_from_db()
            else:
                self.logger.info("File already downloaded by this system: {} - {}".format(vid.title, vid.__dict__))
            db_session.remove()

        else:
            db_session.remove()
            youtube_keys = load_keys(1)
            self.logger.info("Grabbing new video information from youtube: {}".format(vid_id))
            response_videos = list_uploaded_videos_videos(youtube_keys[0], [vid_id], 1)
            if len(response_videos) > 0:
                video = response_videos[0]
                video.vid_path = vid_path
                video.downloaded = True
                video.watched = False
                video.date_downloaded = datetime.datetime.utcnow()
                self.logger.info("Downloading thumbnail: {} - {}".format(video.title, video.__dict__))
                download_thumbnails_threaded([video])
                self.logger.info("Adding new file to db: {} - {}".format(video.title, video.__dict__))
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
