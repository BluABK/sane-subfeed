import os
import sys
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMenu, QAction

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.default_application_handler import open_with_default_application
from sane_yt_subfeed.gui.views.grid_view.play_view.play_thumbnail_tile import PlayThumbnailTile
from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.gui.dialogs.sane_text_view_dialog import SaneTextViewDialog


class PlayTile(VideoTile):

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        super().__init__(parent, video, vid_id, clipboard, status_bar)
        self.logger = create_logger(__name__)
        self.root = parent.root
        self.parent = parent

    def init_thumbnailtile(self):
        return PlayThumbnailTile(self)

    def mousePressEvent(self, QMouseEvent):  # FIXME: Make mouse hotkeys based on hotkeys.ini
        """
        Override mousePressEvent to support mouse button actions
        :param QMouseEvent:
        :return:
        """
        if QMouseEvent.button() == Qt.MidButton:
            self.decrease_prio()
        elif QMouseEvent.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.decrease_prio()
        elif QMouseEvent.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.AltModifier:
            self.mark_discarded()
        elif QMouseEvent.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            self.config_play_video(self.video.vid_path, self.get_default_player(), mark_watched=False)
        elif QMouseEvent.button() == Qt.LeftButton:
            self.config_play_video(self.video.vid_path, self.get_default_player())

    def get_default_player(self):
        config_default_player = self.str_to_list(read_config('Player', 'default_player', literal_eval=False))
        if config_default_player:
            return config_default_player
        else:
            return None

    def config_play_video(self, file_path, player, mark_watched=True):
        if read_config('Play', 'use_url_as_path'):
            file_path = self.video.url_video
            player = read_config('Player', 'url_player', literal_eval=False)
        self.play_vid(file_path, player, mark_watched=mark_watched)

    def play_vid(self, file_path, player, mark_watched=True):
        if mark_watched:
            self.mark_watched()
        self.logger.info('Playing {}, with player: {}'.format(file_path, player))
        if not os.path.isfile(file_path):
            self.logger.warning('os.path.isfile returns False for File: {}'.format(file_path))
        if player:
            popen_args = player + [file_path]
            subprocess.Popen(popen_args)
        else:
            subprocess.Popen([file_path], shell=True)

    def str_to_list(self, s):
        """
        Transform a space delimited string to a list of substrings.
        Returns s as-is if False.
        :param s:
        :return:
        """
        if s:
            return s.split(' ')
        else:
            return s

    def str_to_list_destructive(self, s):
        """
        Destructively transform a space delimited string to a list of substrings.
        Does nothing If string is False.
        :param s:
        :return:
        """
        if s:
            s = s.split(' ')

    @staticmethod
    def determine_name(name, failover_name):
        if name:
            return name
        else:
            return failover_name

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
        url_player = self.str_to_list(read_config('Player', 'url_player', literal_eval=False))
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
                                "Play with url player"))

        if not self.video.vid_path:
            download_video = menu.addAction("Download video")
        else:
            download_video = None

        menu.addSeparator()
        show_description_dialog = menu.addAction("View description")
        open_thumbnail_file = menu.addAction("View image")
        if read_config('Debug', 'debug'):
            menu.addSeparator()
            debug_log_video_obj = menu.addAction("Send to logger")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            self.copy_url()
        elif action == discard_item_action:
            self.mark_discarded()
        elif action == watch_item_action:
            self.mark_watched()
        elif action == play_wo_action:
            self.config_play_video(self.video.vid_path, self.get_default_player(), mark_watched=False)
        elif action == alternative_player1_action and alternative_player1_action:
            self.play_vid(self.video.vid_path, alternative_player1)
        elif action == alternative_player2_action and alternative_player2_action:
            self.play_vid(self.video.vid_path, alternative_player2)
        elif action == alternative_player3_action and alternative_player3_action:
            self.play_vid(self.video.vid_path, alternative_player3)
        elif action == alternative_player4_action and alternative_player4_action:
            self.play_vid(self.video.vid_path, alternative_player4)
        elif action == alternative_player5_action and alternative_player5_action:
            self.play_vid(self.video.vid_path, alternative_player5)
        elif action == alternative_player6_action and alternative_player6_action:
            self.play_vid(self.video.vid_path, alternative_player6)
        elif action == alternative_player7_action and alternative_player7_action:
            self.play_vid(self.video.vid_path, alternative_player7)
        elif action == alternative_player8_action and alternative_player8_action:
            self.play_vid(self.video.vid_path, alternative_player8)
        elif action == alternative_player9_action and alternative_player9_action:
            self.play_vid(self.video.vid_path, alternative_player9)
        elif action == alternative_player10_action and alternative_player10_action:
            self.play_vid(self.video.vid_path, alternative_player10)
        elif action == url_player_action:
            self.play_vid(self.video.url_video, url_player)
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

    def old_videos(self, vid_age):
        pass
