import subprocess

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication

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
            self.play_vid(self.video.vid_path)


    def play_vid(self, file_path, player="mpc-hc64"):
        subprocess.Popen([player, file_path])