import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from sane_yt_subfeed.config_handler import read_config
# from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.database.detached_models.video_d import VideoD
# import sane_yt_subfeed.controller.listeners.gui.views.grid_view.static_grid_view_listener as static_grid_view_listener


class GridViewListener(QObject):

    def __init__(self, model):
        """
        Structure/Model for GridViewListeners to inherit.
        :param model:
        """
        super().__init__()
        self.model = model
        self.name = 'GridViewListener'
        self.logger = create_logger(__name__ + '.' + self.name)
        self.videos_limit = model.videos_limit

    def scroll_reached_end(self):
        """
        Reaction to a GridView scrollbar reaching the end.

        If there are more videos in the list, load a videos_limit amount of them.
        :return:
        """
        add_value = read_config("Model", "loaded_videos")
        self.model.videos_limit = self.model.videos_limit + add_value
        self.update_from_db()

    def update_from_db(self):
        """
        Update video list from DB.

        self.model.update_<view>_videos_from_db()
        :return:
        """
        self.logger.critical("DUMMY FUNCTION: Override in inheritance")

    def thumbnail_download(self):
        """
        Updates downloaded thumbnails.
        :return:
        """
        self.model.update_thumbnails()
        self.logger.debug("Updating thumbnails complete")
        self.videos_updated()

    def download_finished_in_db(self):
        """
        Action to take if tile has been flagged as downloaded (DB version).
        :return:
        """
        self.update_from_db()

    def videos_changed(self):
        """
        Emits a signal that video list has been modified, usual response is to reload feed.

        self.videosChanged.emit()
        :return:
        """
        self.logger.critical("DUMMY FUNCTION: Override in inheritance")

    def videos_updated(self):
        """
        Emits a signal that videos in the list have been modified, usual response is to redraw videos.

        self.videosUpdated.emit()
        :return:
        """
        self.logger.critical("DUMMY FUNCTION: Override in inheritance")

    def redraw_videos(self, video):
        """
        Issue a redraw of one of more video tiles.

        self.redrawVideos.emit([video])
        :param video:
        :return:
        """
        self.logger.critical("DUMMY FUNCTION: Override in inheritance")

    def update_and_redraw_tiles(self, video):
        """
        Common operations for tiles.
        :param video:
        :return:
        """
        # Update a Grid View
        self.videos_changed()
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True).start()
        # Update a GridView from database.
        #self.update_from_db()
        # Redraw the video
        # self.redraw_videos(video)
        # # FIXME: Reload GridView from DB (or dismissed tiles shows right back up)
        # self.update_from_db()

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

