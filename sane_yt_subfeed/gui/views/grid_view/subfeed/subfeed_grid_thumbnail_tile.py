import os
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap

from sane_yt_subfeed.absolute_paths import ICONS_PATH, RESOURCES_PATH
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.grid_view.thumbnail_tile import ThumbnailTile
from sane_yt_subfeed.log_handler import create_logger

OVERLAY_NEW_PATH = os.path.join(ICONS_PATH, 'new_vid.png')
OVERLAY_MISSED_PATH = os.path.join(ICONS_PATH, 'missed_vid.png')
OVERLAY_DOWNLOADED_PATH = os.path.join(ICONS_PATH, 'downloaded_vid.png')
OVERLAY_DISCARDED_PATH = os.path.join(ICONS_PATH, 'dismissed.png')
OVERLAY_WATCHED_PATH = os.path.join(ICONS_PATH, 'watched.png')
THUMBNAIL_NA_PATH = os.path.join(RESOURCES_PATH, 'thumbnail_na.png')


class SubfeedGridViewThumbnailTile(ThumbnailTile):

    def __init__(self, parent):
        super().__init__(parent)
        self.logger = create_logger(__name__)

    def add_overlay(self, painter, thumb):
        """
        Override inherited class to set custom overlay labels on thumbnail tiles.

        Since only one overlay can be clearly displayed at a time it checks which to set
        through a set of if cases ranking highest to lowest priority label.
        :param painter:
        :param thumb:
        :return:
        """
        # Overlay conditions
        watched = read_config('GridView', 'show_watched') and self.parent.video.watched
        dismissed = read_config('GridView', 'show_dismissed') and self.parent.video.discarded
        downloaded = read_config('SubFeed', 'show_downloaded') and self.parent.video.downloaded
        missed = self.parent.video.missed
        new = self.parent.video.new

        if downloaded or watched or dismissed or missed or new:
            if self.parent.video.downloaded:
                overlay = QPixmap(OVERLAY_DOWNLOADED_PATH)
            elif self.parent.video.watched:
                overlay = QPixmap(OVERLAY_WATCHED_PATH)
            elif self.parent.video.discarded:
                overlay = QPixmap(OVERLAY_DISCARDED_PATH)
            elif missed:
                    overlay = QPixmap(OVERLAY_MISSED_PATH)
            else:
                    overlay = QPixmap(OVERLAY_NEW_PATH)

            resize_ratio = min(thumb.width() * 0.7 / thumb.width(), thumb.height() * 0.3 / thumb.height())
            new_size = QSize(thumb.width() * resize_ratio, thumb.height() * resize_ratio)
            overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            point = QPoint(thumb.width() - overlay.width(), 0)
            painter.drawPixmap(point, overlay)