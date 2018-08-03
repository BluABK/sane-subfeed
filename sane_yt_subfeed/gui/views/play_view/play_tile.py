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
        config_default_player = read_config('Player', 'default_player')
        if config_default_player == "":
            return None
        else:
            return config_default_player


    def play_vid(self, file_path, player):
        self.mark_watched()
        if player:
            subprocess.Popen([player, file_path])
        else:
            subprocess.Popen([file_path])



    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
        menu = QMenu(self)
        copy_url_action = menu.addAction("Copy link")
        discard_item_action = menu.addAction("Discard video")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            self.copy_url()
        elif action == discard_item_action:
            self.mark_discarded()