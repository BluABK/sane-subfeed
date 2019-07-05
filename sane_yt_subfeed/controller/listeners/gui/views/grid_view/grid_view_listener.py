import os

from PyQt5.QtCore import QObject, pyqtSlot

from sane_yt_subfeed.handlers.config_handler import read_config
# from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.handlers.log_handler import create_logger
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
        self.widget_id = None
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
        pass

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
        pass

    def videos_updated(self):
        """
        Emits a signal that videos in the list have been modified, usual response is to redraw videos.

        self.videosUpdated.emit()
        :return:
        """
        pass

    def redraw_video(self, video: VideoD):
        """
        Issue a redraw of a video tile.
        :param video:
        :return:
        """
        pass

    def redraw_videos(self, video):
        """
        Issue a redraw of one of more video tiles.

        self.redrawVideos.emit([video])
        :param video:
        :return:
        """
        pass

    def repaint_video(self, video: VideoD):
        """
        Issue a repaint (re-pixmap) of a video tile.
        :param video:
        :return:
        """
        pass

    def repaint_videos(self, videos: list):
        """
        Issue a redraw of one of more video tiles.
        :param videos:
        :return:
        """
        pass

    def update_and_repaint_tile(self, video):
        """
        Common operations for tiles.
        :param video:
        :return:
        """
        # Update a Grid View
        self.videos_changed()
        # Update Video in Database with the changed attributes
        UpdateVideo(video, update_existing=True).start()
        if read_config('GridView', 'show_dismissed'):
            # Update a GridView from database.
            self.update_from_db()
            # Repaint the video thumbnail pixmap
            self.repaint_video(video)

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
        if read_config('GridView', 'show_dismissed'):
            # Update a GridView from database.
            self.update_from_db()
            # Redraw the video
            self.redraw_videos(video)

    @pyqtSlot(VideoD)
    def tile_watched(self, video: Video):
        """
        Action to take if tile has been flagged as watched.

        Called by Views: Playback
        :param video:
        :return:
        """
        video.watched = True
        if not read_config('GridView', 'show_watched'):
            self.logger.info("Mark watched: {} - {}".format(video.title, video.__dict__))
            self.model.hide_video_item(video, self.widget_id)
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_unwatched(self, video: Video):
        """
        Action to take if tile has been un-flagged as watched.

        Called by Views: Playback
        :param video:
        :return:
        """
        video.watched = False
        if not read_config('GridView', 'show_watched'):
            self.logger.info("Mark unwatched: {} - {}".format(video.title, video.__dict__))
            self.model.unhide_video_item(video, self.widget_id)
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_discarded(self, video: Video):
        """
        Action to take if tile has been flagged as dismissed.

        Called by Views: Subfeed and Playback
        :param video:
        :return:
        """
        video.discarded = True
        if not read_config('GridView', 'show_dismissed'):
            self.logger.info("Hide video (Discarded): {}".format(video))
            self.model.hide_video_item(video, self.widget_id)
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_undiscarded(self, video: Video):
        """
        Action to take if tile has been un-flagged as dismissed.

        Called by Views: Subfeed and Playback
        :param video:
        :return:
        """
        video.discarded = False
        if not read_config('GridView', 'show_dismissed'):
            self.logger.info("Un-hide video (Un-discarded): {}".format(video))
            self.model.unhide_video_item(video, self.widget_id)
        self.update_and_repaint_tile(video)

    @pyqtSlot(VideoD)
    def tile_delete_downloaded_data(self, video: Video):
        """
        Action to take if tile has been told to delete its downloaded data.

        This will delete the video file.
        :param video:
        :return:
        """

        # Delete downloaded video file
        os.remove(video.vid_path)
        self.logger.info("Deleted: {}".format(video.vid_path))

        # Unset path to signal that the data isn't on disk.
        video.vid_path = None

        # Repaint the tile to reflect the action.
        self.update_and_repaint_tile(video)
