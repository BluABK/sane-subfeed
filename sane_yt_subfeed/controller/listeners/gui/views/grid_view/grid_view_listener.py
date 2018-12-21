import gc
import time

from PyQt5.QtCore import *  # FIXME: imp *

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.database.detached_models.video_d import VideoD


import sane_yt_subfeed.controller.listeners.gui.views.grid_view.static_grid_view_listener as static_grid_view_listener


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

        # Assign myself to the static listener in order to communicate with DownloadView.
        static_grid_view_listener.STATIC_GRID_VIEW_LISTENER = self

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
            "Hide video(Downloading): {}".format(video))
        video.downloaded = True
        self.model.hide_video_item(video)
        self.hiddenVideosChanged.emit()
        DownloadViewListener.download_video(video,
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
        # Reload GridView from DB (or dismissed tiles shows right back up)
        self.update_from_db()

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
        # Reload GridView from DB (or dismissed tiles shows right back up)
        self.update_from_db()

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
        self.logger.info("Hide video (Discarded): {}".format(video))
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
        self.logger.info("Un-hide video (Un-discarded): {}".format(video))
        video.discarded = False
        self.model.unhide_video_item(video)
        self.playback_tile_update_and_redraw(video)
        self.subfeed_tile_update_and_redraw(video)

    def run(self):
        while True:
            time.sleep(2)
