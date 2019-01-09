from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QApplication

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.default_application_handler import open_with_default_application
from sane_yt_subfeed.gui.dialogs.sane_text_view_dialog import SaneTextViewDialog
from sane_yt_subfeed.gui.views.grid_view.subfeed.subfeed_grid_thumbnail_tile import SubfeedGridViewThumbnailTile
from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile
from sane_yt_subfeed.database.detached_models.video_d import VIDEO_KIND_VOD, VIDEO_KIND_LIVE, \
    VIDEO_KIND_LIVE_SCHEDULED, VIDEO_KIND_PREMIERE
from sane_yt_subfeed.log_handler import create_logger

VIDEO_IS_LIVE_TITLE = "This video is live broadcast content!"
VIDEO_IS_LIVE_MSG = "If you proceed to download this video is will be streamed in realtime and not finish until the" \
                    "stream ends."

class SubfeedGridViewTile(VideoTile):

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        super().__init__(parent, video, vid_id, clipboard, status_bar)
        self.logger = create_logger(__name__)

    def init_thumbnail_tile(self):
        return SubfeedGridViewThumbnailTile(self)

    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
        menu = QMenu(self)
        copy_url_action = menu.addAction("Copy link")
        downloaded_item_action = menu.addAction("Copy link and mark as downloaded")
        discard_item_action = menu.addAction("Dismiss video")

        menu.addSeparator()
        show_description_dialog = menu.addAction("View description")
        open_thumbnail_file = menu.addAction("View image")
        if read_config('Debug', 'debug'):
            menu.addSeparator()
            debug_log_video_obj = menu.addAction("Send to logger")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if self.video.kind is VIDEO_KIND_VOD:
            if action == copy_url_action:
                self.copy_url()
            elif action == downloaded_item_action:
                self.mark_downloaded()
            elif action == discard_item_action:
                self.mark_discarded()
        elif self.video.kind is VIDEO_KIND_LIVE or self.video.kind is VIDEO_KIND_LIVE_SCHEDULED:
            if action == copy_url_action:
                self.copy_url()
            elif action == discard_item_action:
                self.mark_discarded()

        if action == open_thumbnail_file:
            open_with_default_application(self.video.thumbnail_path)
        elif action == show_description_dialog:
            description_dialog = SaneTextViewDialog(self.parent, self.video.description)
            description_dialog.setWindowTitle("Video description for: {} - {}".format(self.video.channel_title,
                                                                                      self.video.title))
            description_dialog.show()

        if read_config('Debug', 'debug'):
            if action == debug_log_video_obj:
                self.logger.debug(self.video.__dict__)

    def mousePressEvent(self, QMouseEvent):
        """
        Override mousePressEvent to support mouse button actions
        :param QMouseEvent:
        :return:
        """
        if self.video.kind is VIDEO_KIND_VOD:
            if QMouseEvent.button() == Qt.MidButton:
                self.mark_discarded()
            elif QMouseEvent.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.logger.error("Not Implemented: Select video")
            elif QMouseEvent.button() == Qt.LeftButton:
                self.mark_downloaded()
        elif self.video.kind is VIDEO_KIND_LIVE or self.video.kind is VIDEO_KIND_LIVE_SCHEDULED:
            if QMouseEvent.button() == Qt.MidButton:
                self.mark_discarded()
            elif QMouseEvent.button() == Qt.LeftButton:
                self.root.confirmation_dialog(VIDEO_IS_LIVE_MSG, self.mark_downloaded, title=VIDEO_IS_LIVE_TITLE,
                                              ok_text="Yes, *stream* it.", cancel_text="Abort, abort, ABORT!")

    def mark_discarded(self):
        """
        Mark the video as discarded (override with correct listener).
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileDiscarded.emit(self.video)
        super().mark_discarded()

    def unmark_discarded(self):
        """
        Mark the video as un-discarded (override with correct listener).
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileUndiscarded.emit(self.video)
        super().unmark_discarded()

    def mark_watched(self):
        """
        Mark the video as watched (override with correct listener).
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileWatched.emit(self.video)
        super().mark_watched()

    def unmark_watched(self):
        """
        Mark the video as Unwatched (override with correct listener).
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileUnwatched.emit(self.video)
        super().unmark_watched()
