from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QMenu

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.handlers.default_application_handler import open_with_default_application
from sane_yt_subfeed.gui.dialogs.sane_text_view_dialog import SaneTextViewDialog
from sane_yt_subfeed.gui.views.grid_view.playback.playback_grid_view_thumbnail_tile import PlaybackGridViewThumbnailTile
from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile
from sane_yt_subfeed.handlers.log_handler import create_logger


class PlaybackGridViewTile(VideoTile):

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        super().__init__(parent, video, vid_id, clipboard, status_bar)
        self.logger = create_logger(__name__)
        self.root = parent.root
        self.parent = parent

    def init_thumbnail_tile(self):
        return PlaybackGridViewThumbnailTile(self)

    def mousePressEvent(self, event: QMouseEvent):  # FIXME: Make mouse hotkeys based on hotkeys.ini
        """
        Override mousePressEvent to support mouse button actions
        :param event:
        :return:
        """
        if event.button() == Qt.MidButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.decrease_prio()
        elif event.button() == Qt.MidButton:
            self.mark_discarded()
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            self.open_in_player(self.video.vid_path, mark_watched=False)
        elif event.button() == Qt.LeftButton:
            self.open_in_player(self.video.vid_path)

    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
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

        if not self.video.vid_path:
            download_video = menu.addAction("Re-download missing video")
        else:
            download_video = None

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
        elif action == discard_item_action:
            self.mark_discarded()
        elif action == watch_item_action:
            self.mark_watched()
        elif action == play_wo_action:
            self.open_in_player(self.video.vid_path, mark_watched=False)
        elif action == alternative_player1_action and alternative_player1_action:
            self.open_in_player(self.video.vid_path, player=alternative_player1)
        elif action == alternative_player2_action and alternative_player2_action:
            self.open_in_player(self.video.vid_path, player=alternative_player2)
        elif action == alternative_player3_action and alternative_player3_action:
            self.open_in_player(self.video.vid_path, player=alternative_player3)
        elif action == alternative_player4_action and alternative_player4_action:
            self.open_in_player(self.video.vid_path, player=alternative_player4)
        elif action == alternative_player5_action and alternative_player5_action:
            self.open_in_player(self.video.vid_path, player=alternative_player5)
        elif action == alternative_player6_action and alternative_player6_action:
            self.open_in_player(self.video.vid_path, player=alternative_player6)
        elif action == alternative_player7_action and alternative_player7_action:
            self.open_in_player(self.video.vid_path, player=alternative_player7)
        elif action == alternative_player8_action and alternative_player8_action:
            self.open_in_player(self.video.vid_path, player=alternative_player8)
        elif action == alternative_player9_action and alternative_player9_action:
            self.open_in_player(self.video.vid_path, player=alternative_player9)
        elif action == alternative_player10_action and alternative_player10_action:
            self.open_in_player(self.video.vid_path, player=alternative_player10)
        elif action == url_player_action:
            self.open_in_browser()
        elif download_video and action == download_video:
            self.mark_downloaded()
        elif action == open_thumbnail_file:
            open_with_default_application(self.video.thumbnail_path)
        elif action == show_description_dialog:
            description_dialog = SaneTextViewDialog(self.parent, self.video.description)
            description_dialog.setWindowTitle("Video description for: {} - {}".format(self.video.channel_title,
                                                                                      self.video.title))
            description_dialog.show()

        if read_config('Debug', 'debug'):
            if action == debug_log_video_obj:
                self.logger.debug(self.video.__dict__)

    def color_old_video(self, vid_age, days=1):
        pass

    def mark_discarded(self):
        """
        Mark the video as discarded (override with correct listener).
        :return:
        """
        self.parent.main_model.playback_grid_view_listener.tileDiscarded.emit(self.video)
        super().mark_discarded()

    def unmark_discarded(self):
        """
        Mark the video as un-discarded (override with correct listener).
        :return:
        """
        self.parent.main_model.playback_grid_view_listener.tileUndiscarded.emit(self.video)
        super().unmark_discarded()

    def mark_watched(self):
        """
        Mark the video as watched (override with correct listener).
        :return:
        """
        self.parent.main_model.playback_grid_view_listener.tileWatched.emit(self.video)
        super().mark_watched()

    def unmark_watched(self):
        """
        Mark the video as Unwatched (override with correct listener).
        :return:
        """
        self.parent.main_model.playback_grid_view_listener.tileUnwatched.emit(self.video)
        super().unmark_watched()

    def decrease_prio(self):
        self.parent.main_model.playback_grid_view_listener.decreaseWatchPrio.emit(self.video)
        super().decrease_prio()

    def increase_prio(self):
        self.parent.main_model.playback_grid_view_listener.increaseWatchPrio.emit(self.video)
        super().increase_prio()
