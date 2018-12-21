from PyQt5.QtCore import pyqtSignal, pyqtSlot

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.controller.listeners.gui.views.grid_view.grid_view_listener import GridViewListener
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.write_operations import UpdateVideo


class PlaybackGridViewListener(GridViewListener):

    # Overridden inherited listeners
    updateFromDb = pyqtSignal()
    scrollReachedEnd = pyqtSignal()
    thumbnailDownload = pyqtSignal()
    redrawVideos = pyqtSignal(list)

    # Own listeners
    videosChanged = pyqtSignal()
    videosUpdated = pyqtSignal()
    decreaseWatchPrio = pyqtSignal(VideoD)
    increaseWatchPrio = pyqtSignal(VideoD)

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        self.name = 'PlaybackGridViewListener'
        self.logger = create_logger(__name__ + '.' + self.name)
        self.videos_limit = model.playview_videos_limit

        # Inherited listeners
        self.tileWatched.connect(self.tile_watched)
        self.tileUnwatched.connect(self.tile_unwatched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.tileUndiscarded.connect(self.tile_undiscarded)

        # Overridden inherited listeners
        self.updateFromDb.connect(self.update_from_db)
        self.thumbnailDownload.connect(self.thumbnail_download)

        # Own listeners
        self.decreaseWatchPrio.connect(self.decrease_watch_prio)
        self.increaseWatchPrio.connect(self.increase_watch_prio)
        self.scrollReachedEnd.connect(self.scroll_reached_end)

    def update_from_db(self):
        """
        Update video list from DB.

        Override which db update function gets called in model here.
        :return:
        """
        self.model.update_playback_videos_from_db()

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
