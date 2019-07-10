from PySide2.QtCore import Signal, Slot

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.handlers.config_handler import read_config
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
    updateFromDb = Signal()
    scrollReachedEnd = Signal()
    thumbnailDownload = Signal()
    tileDiscarded = Signal(VideoD)
    tileUndiscarded = Signal(VideoD)
    tileWatched = Signal(VideoD)
    tileUnwatched = Signal(VideoD)
    tileDeleteDownloadedData = Signal(VideoD)
    videosChanged = Signal()
    videosUpdated = Signal()
    tileDownloaded = Signal(VideoD)
    decreaseWatchPrio = Signal(VideoD)
    increaseWatchPrio = Signal(VideoD)

    # Defined in grid_view.py inheritance
    redrawVideos = Signal(list)
    redrawVideo = Signal(VideoD)
    repaintVideos = Signal(list)
    repaintVideo = Signal(VideoD)

    # FIXME: move youtube-dl listener to its own listener?
    downloadFinished = Signal(VideoD)
    # FIXME: move to db listener?
    downloadedVideosChangedinDB = Signal()

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

        # Connect shared listeners
        self.tileWatched.connect(self.tile_watched)
        self.tileUnwatched.connect(self.tile_unwatched)
        self.tileDiscarded.connect(self.tile_discarded)
        self.tileUndiscarded.connect(self.tile_undiscarded)
        self.tileDeleteDownloadedData.connect(self.tile_delete_downloaded_data)

        # Connect own listeners
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
        Emits a Signal that video list has been modified, usual response is to reload feed.
        :return:
        """
        self.videosChanged.emit()

    def videos_updated(self):
        """
        Emits a Signal that videos in the list have been modified, usual response is to redraw videos.
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

    # noinspection PyCallingNonCallable
    @Slot(VideoD)
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

    # noinspection PyCallingNonCallable
    @Slot(VideoD)
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

    # noinspection PyCallingNonCallable
    @Slot(VideoD)
    def tile_downloaded(self, video: VideoD):
        """
        Action to take if tile has been flagged as downloaded.
        :param video:
        :return:
        """
        video.downloaded = True
        if not read_config('SubFeed', 'show_downloaded'):
            self.logger.info("Hide video(Downloading): {}".format(video))
            self.model.hide_video_item(video, SUBFEED_VIEW_ID)
        else:
            self.model.subfeed_grid_view_listener.redraw_video(video)
        # Update Subfeed View to remove video from its grid feed
        self.model.subfeed_grid_view_listener.videosChanged.emit()
        # Update Playback View to add video to its grid feed
        self.videosChanged.emit()
        DownloadViewListener.download_video(video, youtube_dl_finished_listener=[self.downloadFinished],
                                            db_update_listeners=[self.downloadedVideosChangedinDB])

    # noinspection PyCallingNonCallable
    @Slot(VideoD)
    def download_finished(self, video: VideoD):
        """
        Action to take when download has finished.
        :param video:
        :return:
        """
        self.redraw_video(video)
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True, finished_listeners=[self.downloadedVideosChangedinDB]).start()
