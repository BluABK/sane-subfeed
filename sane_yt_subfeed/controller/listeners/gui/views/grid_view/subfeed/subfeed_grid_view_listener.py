from PyQt5.QtCore import pyqtSignal, pyqtSlot

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.controller.listeners.gui.views.grid_view.grid_view_listener import GridViewListener
from sane_yt_subfeed.database.detached_models.video_d import VideoD


class SubfeedGridViewListener(GridViewListener):

    # Overridden inherited listeners
    updateFromDb = pyqtSignal()
    scrollReachedEnd = pyqtSignal()
    thumbnailDownload = pyqtSignal()
    redrawVideos = pyqtSignal(list)

    # Own listeners
    videosChanged = pyqtSignal()
    videosUpdated = pyqtSignal()
    tileDownloaded = pyqtSignal(VideoD)

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        self.name = 'SubfeedGridViewListener'
        self.logger = create_logger(__name__ + '.' + self.name)
        self.videos_limit = model.videos_limit

        # Inherited listeners
        self.tileWatched.connect(self.tile_watched)
        self.tileUnwatched.connect(self.tile_unwatched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.tileUndiscarded.connect(self.tile_undiscarded)

        # Overridden inherited listeners
        self.updateFromDb.connect(self.update_from_db)
        self.thumbnailDownload.connect(self.thumbnail_download)

        # Own listeners
        self.tileDownloaded.connect(self.tile_downloaded)
        self.scrollReachedEnd.connect(self.scroll_reached_end)

    def update_from_db(self):
        """
        Update video list from DB..

        Override which db update function gets called in model here.
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
        DownloadViewListener.download_video(video, youtube_dl_finished_listener=[self.downloadFinished],
                                            db_update_listeners=[self.downloadedVideosChangedinDB])
        self.videosChanged.emit()
