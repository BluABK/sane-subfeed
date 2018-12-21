import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.database.detached_models.video_d import VideoD
import sane_yt_subfeed.controller.listeners.gui.views.grid_view.static_grid_view_listener as static_grid_view_listener


class GridViewListener(QObject):
    static_self = None

    # Listeners
    tileDiscarded = pyqtSignal(VideoD)
    tileUndiscarded = pyqtSignal(VideoD)
    tileWatched = pyqtSignal(VideoD)
    tileUnwatched = pyqtSignal(VideoD)

    updateFromDb = pyqtSignal()
    scrollReachedEnd = pyqtSignal()
    thumbnailDownload = pyqtSignal()

    # Function defined in gui grid_view.py
    redrawVideos = pyqtSignal(list)

    # FIXME: move youtube-dl listener to its own listener?
    downloadFinished = pyqtSignal(VideoD)
    # FIXME: move to db listener?
    downloadedVideosChangedinDB = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.name = 'GridViewListener'
        self.logger = create_logger(__name__ + '.' + self.name)
        self.videos_limit = model.videos_limit

        GridViewListener.static_self = self

        # Assign myself to the static listener in order to communicate with DownloadView.
        static_grid_view_listener.STATIC_GRID_VIEW_LISTENER = self

        self.downloadFinished.connect(self.download_finished)
        self.downloadedVideosChangedinDB.connect(self.download_finished_in_db)

    def scroll_reached_end(self):
        """
        Reaction to a GridView scrollbar reaching the end.

        If there are more videos in the list, load a videos_limit amount of them.
        :return:
        """
        add_value = read_config("Model", "loaded_videos")
        self.model.videos_limit = self.model.videos_limit + add_value
        # If inherited: Add update video list from db logic here
        self.update_from_db()

    def update_from_db(self):
        """
        Update video list from DB.
        :return:
        """
        # self.model.update_playback_videos_from_db()
        self.logger.critical("DUMMY FUNCTION: Override in inheritance")

    def thumbnail_download(self):
        """
        Updates downloaded thumbnails.
        :return:
        """
        self.model.update_thumbnails()
        self.logger.debug("Updating thumbnails complete")
        # If inherited: Add update *VideosUpdated emitter logic here
        self.videosUpdated.emit()

    def download_finished_in_db(self):
        """
        Action to take if tile has been flagged as downloaded (DB version).
        :return:
        """
        self.update_from_db()

    def update_and_redraw_tiles(self, video: Video):
        """
        Common operations for Playback tiles.
        :param video:
        :return:
        """
        # Update a Grid View
        self.videosChanged.emit()
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True).start()
        # Update a GridView from database.
        self.update_from_db()
        # Redraw the video
        self.redrawVideos.emit([video])
        # FIXME: Reload GridView from DB (or dismissed tiles shows right back up)
        self.update_from_db()

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
        self.update_and_redraw_tiles(video)

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
        self.update_and_redraw_tiles(video)

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
        self.update_and_redraw_tiles(video)

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
        self.update_and_redraw_tiles(video)

    def run(self):
        while True:
            time.sleep(2)
