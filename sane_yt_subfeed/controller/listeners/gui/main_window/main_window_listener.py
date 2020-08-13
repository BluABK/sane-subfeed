import gc
import time
import re

from PyQt5.QtCore import *

from sane_yt_subfeed import main
from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.exceptions.sane_aborted_operation import SaneAbortedOperation
from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded
from sane_yt_subfeed.youtube.update_videos import load_keys
from sane_yt_subfeed.youtube.youtube_requests import get_remote_subscriptions_cached_oauth, \
    list_uploaded_videos_videos, add_subscription

YOUTUBE_URL_PATTERN = '(http[s]?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)?' \
                      '([0-9A-Za-z_-]{10}[048AEIMQUYcgkosw])'


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
        self.model.update_subfeed_videos_from_remote(refresh_type=refresh_type)

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
        reggie = re.match(YOUTUBE_URL_PATTERN, video_url)
        video_id = reggie.groups()[-1]
        self.logger.debug("{} --> ID: {}".format(video_url, video_id))
        video_d = list_uploaded_videos_videos(load_keys(1)[0], [video_id], 50)[0]
        download_thumbnails_threaded([video_d])
        DownloadViewListener.download_video(video_d,
                                            youtube_dl_finished_listener=[
                                                self.model.playback_grid_view_listener.downloadFinished],
                                            db_update_listeners=[
                                                self.model.playback_grid_view_listener.downloadedVideosChangedinDB])

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
