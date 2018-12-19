import os

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap

from sane_yt_subfeed.absolute_paths import ICONS_PATH, RESOURCES_PATH
from sane_yt_subfeed.gui.views.grid_view.thumbnail_tile import ThumbnailTile
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.config_handler import read_config


OVERLAY_NO_FILE_PATH = os.path.join(ICONS_PATH, 'no_file.png')
OVERLAY_DISMISSED_PATH = os.path.join(ICONS_PATH, 'dismissed.png')
OVERLAY_WATCHED_PATH = os.path.join(ICONS_PATH, 'watched.png')
THUMBNAIL_NA_PATH = os.path.join(RESOURCES_PATH, 'thumbnail_na.png')


class PlaybackGridViewThumbnailTile(ThumbnailTile):

    def __init__(self, parent):
        super().__init__(parent)
        self.logger = create_logger(__name__)

    def add_overlay(self, painter, thumb):
        url_as_path = read_config('Play', 'use_url_as_path')
        show_watched = read_config('GridView', 'show_watched')
        show_dismissed = read_config('GridView', 'show_dismissed')

        if ((not self.parent.video.vid_path) and not url_as_path) or (self.parent.video.watched and show_watched) \
                or (self.parent.video.discarded and show_dismissed):
            if not self.parent.video.vid_path:
                overlay = QPixmap(OVERLAY_NO_FILE_PATH)
            elif self.parent.video.watched:
                overlay = QPixmap(OVERLAY_WATCHED_PATH)
            else:
                overlay = QPixmap(OVERLAY_DISMISSED_PATH)
            resize_ratio = min(thumb.width() * 0.7 / thumb.width(), thumb.height() * 0.3 / thumb.height())
            new_size = QSize(thumb.width() * resize_ratio, thumb.height() * resize_ratio)
            overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            point = QPoint(thumb.width() - overlay.width(), 0)
            painter.drawPixmap(point, overlay)
