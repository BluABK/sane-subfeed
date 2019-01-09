from PyQt5.QtCore import pyqtSignal, pyqtSlot

from sane_yt_subfeed import create_logger
# from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view/_listener import DownloadViewListener
from sane_yt_subfeed.controller.listeners.gui.views.grid_view.grid_view_listener import GridViewListener
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.controller.static_controller_vars import SUBFEED_VIEW_ID
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.detached_models.video_d import VIDEO_KIND_VOD, VIDEO_KIND_LIVE, \
    VIDEO_KIND_LIVE_SCHEDULED, VIDEO_KIND_PREMIERE


class SubfeedGridViewListener(GridViewListener):
    # Shared Listeners
    tileDiscarded = pyqtSignal(VideoD)
    tileUndiscarded = pyqtSignal(VideoD)
    tileWatched = pyqtSignal(VideoD)
    tileUnwatched = pyqtSignal(VideoD)

    # Own listeners
    tileMarkedPremiere = pyqtSignal(VideoD)
    tileUnmarkedPremiere = pyqtSignal(VideoD)
    tileMarkedLivestreamUpcoming = pyqtSignal(VideoD)
    tileUnmarkedLivestreamUpcoming = pyqtSignal(VideoD)
    tileMarkedLivestream = pyqtSignal(VideoD)
    tileUnmarkedLivestream = pyqtSignal(VideoD)

    videosChanged = pyqtSignal()
    videosUpdated = pyqtSignal()
    updateFromDb = pyqtSignal()
    scrollReachedEnd = pyqtSignal()
    thumbnailDownload = pyqtSignal()

    # Defined in grid_view.py inheritance
    redrawVideos = pyqtSignal(list)
    redrawVideo = pyqtSignal(VideoD)
    repaintVideos = pyqtSignal(list)
    repaintVideo = pyqtSignal(VideoD)

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        self.widget_id = SUBFEED_VIEW_ID
        self.name = 'SubfeedGridViewListener'
        self.logger = create_logger(__name__ + '.' + self.name)
        self.videos_limit = model.videos_limit

        # Connect shared listeners
        self.tileWatched.connect(self.tile_watched)
        self.tileUnwatched.connect(self.tile_unwatched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.tileUndiscarded.connect(self.tile_undiscarded)

        # Connect own listeners
        self.tileMarkedPremiere.connect(self.tile_marked_premiere)
        self.tileUnmarkedPremiere.connect(self.tile_unmarked_premiere)
        self.tileMarkedLivestreamUpcoming.connect(self.tile_marked_livestream_upcoming)
        self.tileUnmarkedLivestreamUpcoming.connect(self.tile_unmarked_livestream_upcoming)
        self.tileMarkedLivestream.connect(self.tile_marked_livestream)
        self.tileUnmarkedLivestream.connect(self.tile_unmarked_livestream)

        self.updateFromDb.connect(self.update_from_db)
        self.thumbnailDownload.connect(self.thumbnail_download)
        self.scrollReachedEnd.connect(self.scroll_reached_end)

    def update_from_db(self):
        """
        Update video list from DB..

        Override which db update function gets called in model here.
        :return:
        """
        self.model.update_subfeed_videos_from_db()

    def videos_changed(self):
        """
        Emits a signal that video list has been modified, usual response is to reload feed.
        :return:
        """
        self.videosChanged.emit()

    def videos_updated(self):
        """
        Emits a signal that videos in the list have been modified, usual response is to redraw videos.
        :return:
        """
        self.videosUpdated.emit()

    def redraw_video(self, video: VideoD):
        """
        Issue a redraw of a video tile.
        :param video:
        :return:
        """
        self.redrawVideo.emit(video)

    def redraw_videos(self, videos: list):
        """
        Issue a redraw of one of more video tiles.
        :param videos:
        :return:
        """
        self.redrawVideos.emit([videos])

    def repaint_video(self, video: VideoD):
        """
        Issue a repaint (re-pixmap) of a video tile.
        :param video:
        :return:
        """
        self.repaintVideo.emit(video)

    def repaint_videos(self, videos: list):
        """
        Issue a redraw of one of more video tiles.
        :param videos:
        :return:
        """
        self.repaintVideos.emit([videos])

    @pyqtSlot(VideoD)
    def tile_marked_premiere(self, video: Video):
        """
        Mark the video as live broadcast content (premiere)

        A premiere is: upcoming stream --> live stream --> vod
        :return:
        """
        video.kind = VIDEO_KIND_PREMIERE
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_unmarked_premiere(self, video: Video):
        """
        Unmark the video as live broadcast content (premiere)

        A premiere is: upcoming stream --> live stream --> vod
        :return:
        """
        video.kind = VIDEO_KIND_VOD
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_marked_livestream_upcoming(self, video: Video):
        """
        Mark the video as live broadcast content (upcoming)
        :return:
        """
        video.kind = VIDEO_KIND_LIVE_SCHEDULED
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_unmarked_livestream_upcoming(self, video: Video):
        """
        Unmark the video as live broadcast content (upcoming)
        :return:
        """
        video.kind = VIDEO_KIND_VOD
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_marked_livestream(self, video: Video):
        """
        Mark the video as live broadcast content (live)
        :return:
        """
        video.kind = VIDEO_KIND_LIVE
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_unmarked_livestream(self, video: Video):
        """
        Unmark the video as live broadcast content (live)
        :return:
        """
        video.kind = VIDEO_KIND_VOD
        self.update_and_repaint_tile(video)
