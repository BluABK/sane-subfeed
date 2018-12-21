from PyQt5.QtCore import pyqtSignal, pyqtSlot

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.controller.listeners.gui.views.grid_view.grid_view_listener import GridViewListener
from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.write_operations import UpdateVideo
import sane_yt_subfeed.controller.listeners.gui.views.grid_view.static_grid_view_listener as static_grid_view_listener
from sane_yt_subfeed.controller.static_controller_vars import PLAYBACK_VIEW_ID, SUBFEED_VIEW_ID


class PlaybackGridViewListener(GridViewListener):
    # Static reference to self used by DownloadViewListenter, MainWindow and YoutubeDownloadListener1
    static_self = None

    # Listeners
    updateFromDb = pyqtSignal()
    scrollReachedEnd = pyqtSignal()
    thumbnailDownload = pyqtSignal()
    redrawVideos = pyqtSignal(list)
    tileDiscarded = pyqtSignal(VideoD)
    tileUndiscarded = pyqtSignal(VideoD)
    tileWatched = pyqtSignal(VideoD)
    tileUnwatched = pyqtSignal(VideoD)
    videosChanged = pyqtSignal()
    videosUpdated = pyqtSignal()
    tileDownloaded = pyqtSignal(VideoD)
    decreaseWatchPrio = pyqtSignal(VideoD)
    increaseWatchPrio = pyqtSignal(VideoD)

    # FIXME: move youtube-dl listener to its own listener?
    downloadFinished = pyqtSignal(VideoD)
    # FIXME: move to db listener?
    downloadedVideosChangedinDB = pyqtSignal()

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        self.widget_id = PLAYBACK_VIEW_ID
        self.name = 'PlaybackGridViewListener'
        self.logger = create_logger(__name__ + '.' + self.name)
        self.videos_limit = model.playview_videos_limit

        GridViewListener.static_self = self

        # Assign myself to the static listener in order to communicate with DownloadView.
        static_grid_view_listener.STATIC_GRID_VIEW_LISTENER = self

        # Listeners
        self.tileWatched.connect(self.tile_watched)
        self.tileUnwatched.connect(self.tile_unwatched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.tileUndiscarded.connect(self.tile_undiscarded)
        self.tileDownloaded.connect(self.tile_downloaded)
        self.downloadFinished.connect(self.download_finished)
        self.downloadedVideosChangedinDB.connect(self.download_finished_in_db)

        self.decreaseWatchPrio.connect(self.decrease_watch_prio)
        self.increaseWatchPrio.connect(self.increase_watch_prio)

        self.updateFromDb.connect(self.update_from_db)
        self.thumbnailDownload.connect(self.thumbnail_download)
        self.scrollReachedEnd.connect(self.scroll_reached_end)

    def update_from_db(self):
        """
        Update video list from DB.

        Override which db update function gets called in model here.
        :return:
        """
        self.model.update_playback_videos_from_db()

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

    def redraw_videos(self, video: VideoD):
        """
        Issue a redraw of one of more video tiles.
        :param video:
        :return:
        """
        self.redrawVideos.emit([video])

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

    @pyqtSlot(VideoD)
    def tile_downloaded(self, video: VideoD):
        """
        Action to take if tile has been flagged as downloaded.
        :param video:
        :return:
        """
        self.logger.info(
            "Hide video(Downloading): {}".format(video))
        video.downloaded = True
        # Hide downloaded/ing video from *Subfeed*
        self.model.hide_video_item(video, SUBFEED_VIEW_ID)
        # Update Playback View to add video to its list
        self.videosChanged.emit()
        DownloadViewListener.download_video(video, youtube_dl_finished_listener=[self.downloadFinished],
                                            db_update_listeners=[self.downloadedVideosChangedinDB])

    @pyqtSlot(VideoD)
    def download_finished(self, video: VideoD):
        """
        Action to take when download has finished.
        :param video:
        :return:
        """
        self.redraw_videos(video)
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True, finished_listeners=[self.downloadedVideosChangedinDB]).start()
