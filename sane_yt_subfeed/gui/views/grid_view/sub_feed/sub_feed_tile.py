import sys
import os
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QApplication
from sane_yt_subfeed.log_handler import create_logger

from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile


class SubFeedTile(VideoTile):

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        super().__init__(parent, video, vid_id, clipboard, status_bar)
        self.logger = create_logger(__name__)

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
        open_thumbnail_file = menu.addAction("View image")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            self.copy_url()
        elif action == downloaded_item_action:
            self.mark_downloaded()
        elif action == discard_item_action:
            self.mark_discarded()
        elif action == open_thumbnail_file:
            try:
                if sys.platform.startswith('linux'):
                    subprocess.call(["xdg-open", self.video.thumbnail_path])
                else:
                    os.startfile(self.video.thumbnail_path)
            except Exception as e_anything:
                self.logger.exception(e_anything)
                pass

    def mousePressEvent(self, QMouseEvent):
        """
        Override mousePressEvent to support mouse button actions
        :param QMouseEvent:
        :return:
        """
        if QMouseEvent.button() == Qt.MidButton:
            self.mark_discarded()
        elif QMouseEvent.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.logger.error("Not Implemented: Select video")
        elif QMouseEvent.button() == Qt.LeftButton:
            self.mark_downloaded()
