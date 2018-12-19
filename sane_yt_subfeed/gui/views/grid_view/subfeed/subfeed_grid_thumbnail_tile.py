import os

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPainter, QPixmap

from sane_yt_subfeed.absolute_paths import ICONS_PATH, RESOURCES_PATH
from sane_yt_subfeed.gui.views.grid_view.thumbnail_tile import ThumbnailTile
from sane_yt_subfeed.log_handler import create_logger


OVERLAY_NEW_PATH = os.path.join(ICONS_PATH, 'new_vid.png')
OVERLAY_MISSED_PATH = os.path.join(ICONS_PATH, 'missed_vid.png')
THUMBNAIL_NA_PATH = os.path.join(RESOURCES_PATH, 'thumbnail_na.png')


class SubfeedGridViewThumbnailTile(ThumbnailTile):

    def __init__(self, parent):
        super().__init__(parent)
        self.logger = create_logger(__name__)

    def add_overlay(self, painter, thumb):
        # show_dismissed = read_config('Play', 'show_dismissed')
        if self.parent.video.missed or self.parent.video.new:
            if self.parent.video.missed:
                overlay = QPixmap(OVERLAY_MISSED_PATH)
            else:
                overlay = QPixmap(OVERLAY_NEW_PATH)
            resize_ratio = min(thumb.width() * 0.7 / thumb.width(), thumb.height() * 0.3 / thumb.height())
            new_size = QSize(thumb.width() * resize_ratio, thumb.height() * resize_ratio)
            overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            point = QPoint(thumb.width() - overlay.width(), 0)
            painter.drawPixmap(point, overlay)
