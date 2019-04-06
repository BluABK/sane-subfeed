from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMenu, QApplication

from sane_yt_subfeed.handlers.config_handler import read_config
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
MOUSE_PRESS_OPEN_URL = 'Open URL in browser'
MOUSE_PRESS_COPY_URL = 'Copy URL'
MOUSE_PRESS_PLAY_URL = 'Open URL in player'
MOUSE_PRESS_DOWNLOAD = 'Download'
MOUSE_PRESS_DOWNLOAD_AND_COPY = 'Download & copy URL'


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
        # Context Menu
        menu = QMenu(self)

        # FIXME: Add a loop that lets you define infinite players in config (see download proxy list method)
        alternative_player1 = self.str_to_list(read_config('Player', 'alternative_player1', literal_eval=False))
        alternative_player2 = self.str_to_list(read_config('Player', 'alternative_player2', literal_eval=False))
        alternative_player3 = self.str_to_list(read_config('Player', 'alternative_player3', literal_eval=False))
        alternative_player4 = self.str_to_list(read_config('Player', 'alternative_player4', literal_eval=False))
        alternative_player5 = self.str_to_list(read_config('Player', 'alternative_player5', literal_eval=False))
        alternative_player6 = self.str_to_list(read_config('Player', 'alternative_player6', literal_eval=False))
        alternative_player7 = self.str_to_list(read_config('Player', 'alternative_player7', literal_eval=False))
        alternative_player8 = self.str_to_list(read_config('Player', 'alternative_player8', literal_eval=False))
        alternative_player9 = self.str_to_list(read_config('Player', 'alternative_player9', literal_eval=False))
        alternative_player10 = self.str_to_list(read_config('Player', 'alternative_player10', literal_eval=False))
        alternative_player1_action = None
        alternative_player2_action = None
        alternative_player3_action = None
        alternative_player4_action = None
        alternative_player5_action = None
        alternative_player6_action = None
        alternative_player7_action = None
        alternative_player8_action = None
        alternative_player9_action = None
        alternative_player10_action = None

        copy_url_action = menu.addAction("Copy link")
        if read_config('Play', 'enabled'):
            downloaded_item_action = menu.addAction("Copy link and download")
        else:
            downloaded_item_action = 'DISABLED'
        discard_item_action = menu.addAction("Dismiss video")
        watch_item_action = menu.addAction("Mark watched")
        play_wo_action = menu.addAction("Play w/o mark watched")

        if alternative_player1:
            alternative_player1_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player1_name', literal_eval=False),
                                    "Play with alternative player 1"))
        if alternative_player2:
            alternative_player2_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player2_name', literal_eval=False),
                                    "Play with alternative player 2"))
        if alternative_player3:
            alternative_player3_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player3_name', literal_eval=False),
                                    "Play with alternative player 3"))
        if alternative_player4:
            alternative_player4_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player4_name', literal_eval=False),
                                    "Play with alternative player 4"))
        if alternative_player5:
            alternative_player5_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player5_name', literal_eval=False),
                                    "Play with alternative player 5"))
        if alternative_player6:
            alternative_player6_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player6_name', literal_eval=False),
                                    "Play with alternative player 6"))
        if alternative_player7:
            alternative_player7_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player7_name', literal_eval=False),
                                    "Play with alternative player 7"))
        if alternative_player8:
            alternative_player8_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player8_name', literal_eval=False),
                                    "Play with alternative player 8"))
        if alternative_player9:
            alternative_player9_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player9_name', literal_eval=False),
                                    "Play with alternative player 9"))
        if alternative_player10:
            alternative_player10_action = menu.addAction(
                self.determine_name(read_config('PlayerFriendlyName', 'alternative_player10_name', literal_eval=False),
                                    "Play with alternative player 10"))

        url_player_action = menu.addAction(
            self.determine_name(read_config('PlayerFriendlyName', 'url_player_name', literal_eval=False),
                                "Open in web browser"))

        # Submenu
        mark_as_live_content_submenu = QMenu(self)
        mark_as_live_content_submenu.setTitle("Mark as liveBroadcastContent")
        menu.addMenu(mark_as_live_content_submenu)
        mark_premiere_action = mark_as_live_content_submenu.addAction("Mark as Premiere")
        mark_livestream_upcoming_action = mark_as_live_content_submenu.addAction("Mark as Scheduled livestream")
        mark_livestream_action = mark_as_live_content_submenu.addAction("Mark as Livestream")
        mark_as_live_content_submenu.addSeparator()
        unmark_live_content_action = mark_as_live_content_submenu.addAction("Unmark as liveBroadcastContent")

        menu.addSeparator()
        show_description_dialog = menu.addAction("View description")
        open_thumbnail_file = menu.addAction("View image")
        if read_config('Debug', 'debug'):
            menu.addSeparator()
            debug_log_video_obj = menu.addAction("Send to logger")

        # Context menu action logic
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            self.copy_url()
        elif action == downloaded_item_action:
            self.mark_downloaded()
        elif action == discard_item_action:
            self.mark_discarded()
        elif action == watch_item_action:
            self.mark_watched()
        elif action == play_wo_action:
            self.open_in_player(self.video.url_video, mark_watched=False, isfile=False)
        elif action == alternative_player1_action and alternative_player1_action:
            self.open_in_player(self.video.url_video, player=alternative_player1, isfile=False)
        elif action == alternative_player2_action and alternative_player2_action:
            self.open_in_player(self.video.url_video, player=alternative_player2, isfile=False)
        elif action == alternative_player3_action and alternative_player3_action:
            self.open_in_player(self.video.url_video, player=alternative_player3, isfile=False)
        elif action == alternative_player4_action and alternative_player4_action:
            self.open_in_player(self.video.url_video, player=alternative_player4, isfile=False)
        elif action == alternative_player5_action and alternative_player5_action:
            self.open_in_player(self.video.url_video, player=alternative_player5, isfile=False)
        elif action == alternative_player6_action and alternative_player6_action:
            self.open_in_player(self.video.url_video, player=alternative_player6, isfile=False)
        elif action == alternative_player7_action and alternative_player7_action:
            self.open_in_player(self.video.url_video, player=alternative_player7, isfile=False)
        elif action == alternative_player8_action and alternative_player8_action:
            self.open_in_player(self.video.url_video, player=alternative_player8, isfile=False)
        elif action == alternative_player9_action and alternative_player9_action:
            self.open_in_player(self.video.url_video, player=alternative_player9, isfile=False)
        elif action == alternative_player10_action and alternative_player10_action:
            self.open_in_player(self.video.url_video, player=alternative_player10, isfile=False)
        elif action == url_player_action:
            self.open_in_browser()

        elif action == mark_premiere_action:
            self.mark_premiere()
        elif action == mark_livestream_upcoming_action:
            self.mark_livestream_upcoming()
        elif action == mark_livestream_action:
            self.mark_livestream()

        # All-in-one tri-state action that unmarks the relevant liveBroadcastContent
        elif action == unmark_live_content_action:
            if self.video.kind == VIDEO_KIND_PREMIERE:
                self.unmark_premiere()
            elif self.video.kind == VIDEO_KIND_LIVE_SCHEDULED:
                self.unmark_livestream_upcoming()
            elif self.video.kind == VIDEO_KIND_LIVE:
                self.unmark_livestream()

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

    def mousePressEvent(self, event: QMouseEvent):
        """
        Override mousePressEvent to support mouse button actions
        :param event:
        :return:
        """
        if self.video.kind == VIDEO_KIND_VOD:
            if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.logger.error("Not Implemented: Select video")
            elif event.button() == Qt.LeftButton:
                left_button_rebind = read_config('SubFeed', 'left_mouse_action', literal_eval=False)

                if left_button_rebind == MOUSE_PRESS_OPEN_URL:
                    self.open_in_browser()
                elif left_button_rebind == MOUSE_PRESS_COPY_URL:
                    self.copy_url(mark_watched=True)
                elif left_button_rebind == MOUSE_PRESS_PLAY_URL:
                    url_player = self.str_to_list(read_config('Player', 'default_player', literal_eval=False))
                    self.open_in_player(self.video.url_video, url_player)
                elif left_button_rebind == MOUSE_PRESS_DOWNLOAD:
                    self.mark_downloaded()
                elif left_button_rebind == MOUSE_PRESS_DOWNLOAD_AND_COPY:
                    self.copy_url()
                    self.mark_downloaded()

            elif event.button() == Qt.MidButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.decrease_prio()
            elif event.button() == Qt.MidButton:
                self.mark_discarded()

        elif self.video.kind == VIDEO_KIND_LIVE or self.video.kind == VIDEO_KIND_LIVE_SCHEDULED \
                or self.video.kind == VIDEO_KIND_PREMIERE:
            if event.button() == Qt.MidButton:
                self.mark_discarded()
            elif event.button() == Qt.LeftButton:
                self.root.confirmation_dialog(VIDEO_IS_LIVE_MSG, self.mark_downloaded, title=VIDEO_IS_LIVE_TITLE,
                                              ok_text="Yes, stream it.",
                                              cancel_text="Abort, abort, ABORT!")

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

    def mark_premiere(self):
        """
        Mark the video as live broadcast content (premiere)

        A premiere is: upcoming stream --> live stream --> vod
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileMarkedPremiere.emit(self.video)
        super().mark_premiere()

    def unmark_premiere(self):
        """
        Unmark the video as live broadcast content (premiere)

        A premiere is: upcoming stream --> live stream --> vod
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileUnmarkedPremiere.emit(self.video)
        super().unmark_premiere()

    def mark_livestream_upcoming(self):
        """
        Mark the video as live broadcast content (upcoming)
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileMarkedLivestreamUpcoming.emit(self.video)
        super().mark_livestream_upcoming()

    def unmark_livestream_upcoming(self):
        """
        Unmark the video as live broadcast content (upcoming)
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileUnmarkedLivestreamUpcoming.emit(self.video)
        super().unmark_livestream_upcoming()

    def mark_livestream(self):
        """
        Mark the video as live broadcast content (live)
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileMarkedLivestream.emit(self.video)
        super().mark_livestream()

    def unmark_livestream(self):
        """
        Unmark the video as live broadcast content (live)
        :return:
        """
        self.parent.main_model.subfeed_grid_view_listener.tileUnmarkedLivestream.emit(self.video)
        super().unmark_livestream()
