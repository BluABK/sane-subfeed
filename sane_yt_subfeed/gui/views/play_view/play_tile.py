import os
import subprocess

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QMenu

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile
from sane_yt_subfeed.log_handler import logger


class PlayTile(VideoTile):

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        super().__init__(parent, video, vid_id, clipboard, status_bar)

    def mousePressEvent(self, QMouseEvent):
        """
        Override mousePressEvent to support mouse button actions
        :param QMouseEvent:
        :return:
        """
        # if QMouseEvent.button() == Qt.MidButton:
        #     self.parent.play_vid(self.video.vid_path)
        if QMouseEvent.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            logger.error("Not Implemented: Select video")
        elif QMouseEvent.button() == Qt.LeftButton:
            self.play_vid(self.video.vid_path, self.get_default_player())

    def get_default_player(self):
        config_default_player = read_config('Player', 'default_player', literal_eval=False)
        if config_default_player:
            return config_default_player
        else:
            return None

    def play_vid(self, file_path, player, mark_watched=True):
        # player = player.strip()
        if mark_watched:
            self.mark_watched()
        if player:
            subprocess.Popen([player, file_path], shell=True)
        else:
            subprocess.Popen([file_path], shell=True)

    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
        menu = QMenu(self)
        copy_url_action = menu.addAction("Copy link")
        discard_item_action = menu.addAction("Discard video(doesn't affect play_view)")

        alternative_player1 = read_config('Player', 'alternative_player1', literal_eval=False)
        alternative_player2 = read_config('Player', 'alternative_player2', literal_eval=False)
        alternative_player3 = read_config('Player', 'alternative_player3', literal_eval=False)
        alternative_player1_action = None
        alternative_player2_action = None
        alternative_player3_action = None

        if alternative_player1:
            alternative_player1_action = menu.addAction("Play with alternative player 1")
        if alternative_player2:
            alternative_player2_action = menu.addAction("Play with alternative player 2")
        if alternative_player3:
            alternative_player3_action = menu.addAction("Play with alternative player 3")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            self.copy_url()
        elif action == discard_item_action:
            self.mark_discarded()
        elif action == alternative_player1_action:
            self.play_vid(self.video.vid_path, alternative_player1)
        elif action == alternative_player2_action:
            self.play_vid(self.video.vid_path, alternative_player2)
        elif action == alternative_player3_action:
            self.play_vid(self.video.vid_path, alternative_player3)


    def old_videos(self, vid_age):
        pass