import os
import sys
import subprocess

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QMenu

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.grid_view.play_view.play_thumbnail_tile import PlayThumbnailTile
from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile
from sane_yt_subfeed.log_handler import logger, create_logger


class PlayTile(VideoTile):

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        super().__init__(parent, video, vid_id, clipboard, status_bar)
        self.logger = create_logger(__name__)

    def init_thumbnailtile(self):
        return PlayThumbnailTile(self)

    def mousePressEvent(self, QMouseEvent):
        """
        Override mousePressEvent to support mouse button actions
        :param QMouseEvent:
        :return:
        """
        # if QMouseEvent.button() == Qt.MidButton:
        #     self.parent.play_vid(self.video.vid_path)
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
        config_default_player = read_config('Player', 'default_player', literal_eval=False)
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
        # player = player.strip()

        if mark_watched:
            self.mark_watched()
        self.logger.info('Playing {}, with player: {}'.format(file_path, player))
        if not os.path.isfile(file_path):
            self.logger.warning('os.path.isfile returns False for File: {}'.format(file_path))
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

        alternative_player1 = read_config('Player', 'alternative_player1', literal_eval=False)
        alternative_player2 = read_config('Player', 'alternative_player2', literal_eval=False)
        alternative_player3 = read_config('Player', 'alternative_player3', literal_eval=False)
        url_player = read_config('Player', 'url_player', literal_eval=False)
        alternative_player1_action = None
        alternative_player2_action = None
        alternative_player3_action = None
        copy_url_action = menu.addAction("Copy link")
        discard_item_action = menu.addAction("Dismiss video")
        watch_item_action = menu.addAction("Mark watched")

        if alternative_player1:
            alternative_player1_action = menu.addAction("Play with alternative player 1")
        if alternative_player2:
            alternative_player2_action = menu.addAction("Play with alternative player 2")
        if alternative_player3:
            alternative_player3_action = menu.addAction("Play with alternative player 3")
        url_player_action = menu.addAction("Play with url player")

        open_thumbnail_file = menu.addAction("View image")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            self.copy_url()
        elif action == discard_item_action:
            self.mark_discarded()
        elif action == watch_item_action:
            self.mark_watched()
        elif action == alternative_player1_action and alternative_player1_action:
            self.play_vid(self.video.vid_path, alternative_player1)
        elif action == alternative_player2_action and alternative_player2_action:
            self.play_vid(self.video.vid_path, alternative_player2)
        elif action == alternative_player3_action and alternative_player3_action:
            self.play_vid(self.video.vid_path, alternative_player3)
        elif action == url_player_action:
            self.play_vid(self.video.url_video, url_player)
        elif action == open_thumbnail_file:
            try:
                if sys.platform.startswith('linux'):
                    subprocess.call(["xdg-open", self.video.thumbnail_path])
                else:
                    os.startfile(self.video.thumbnail_path)
            except Exception as e_anything:
                self.logger.exception(e_anything)
                pass


    def old_videos(self, vid_age):
        pass
