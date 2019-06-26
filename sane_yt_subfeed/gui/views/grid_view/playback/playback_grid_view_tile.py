from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QMenu

from sane_yt_subfeed.handlers.config_handler import read_config, get_valid_options
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

        copy_url_action = menu.addAction("Copy link")
        discard_item_action = menu.addAction("Dismiss video")
        watch_item_action = menu.addAction("Mark watched")
        play_wo_action = menu.addAction("Play w/o mark watched")

        # Get a list of user-defined (valid) alternative players and their custom names.
        alternative_players = self.list_to_str_lists(get_valid_options('AlternativePlayers'))
        alternative_names = get_valid_options('AlternativePlayerNames')

        # Define QActions for each user-defined alternative player.
        alternative_player_actions = []
        if len(alternative_players) > 0:
            for player_index in range(len(alternative_players)):
                # If there are sufficient valid alternative player names use them.
                if len(alternative_names) > player_index:
                    alternative_player_actions.append(menu.addAction(alternative_names[player_index]))
                # If not, use the fail-over.
                else:
                    alternative_player_actions.append(menu.addAction(
                        "Play with UNNAMED alternative player {}".format(player_index)))

        url_player_action = menu.addAction(
            self.determine_name(read_config('PlayerNames', 'url_player_name', literal_eval=False),
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
        elif action in alternative_player_actions:
            # Get the index of action in the list of alt player actions, which corresponds with the list of alt players.
            selected_alternative_player = alternative_players[alternative_player_actions.index(action)]

            # Open video in selected (alternative) player.
            self.open_in_player(self.video.vid_path, player=selected_alternative_player)
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
