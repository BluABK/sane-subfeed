import os

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPainter, QPixmap

from sane_yt_subfeed.gui.views.grid_view.thumbnail_tile import ThumbnailTile
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.config_handler import read_config

OS_PATH = os.path.dirname(__file__)
ICONS_PATH = os.path.join(OS_PATH, '..', '..', '..', 'icons')
RESOURCES_PATH = os.path.join(OS_PATH, '..', '..', '..', '..', 'resources')

OVERLAY_NO_FILE_PATH = os.path.join(ICONS_PATH, 'no_file.png')
OVERLAY_DISMISSED_PATH = os.path.join(ICONS_PATH, 'dismissed.png')
OVERLAY_WATCHED_PATH = os.path.join(ICONS_PATH, 'watched.png')
THUMBNAIL_NA_PATH = os.path.join(RESOURCES_PATH, 'thumbnail_na.png')


class PlayThumbnailTile(ThumbnailTile):

    def __init__(self, parent):
        super().__init__(parent)
        self.logger = create_logger(__name__)

    def add_overlay(self, painter, thumb):
        url_as_path = read_config('Play', 'use_url_as_path')
        show_watched = read_config('GridView', 'show_watched')
        show_dismissed = read_config('GridView', 'show_dismissed')
        if ((not self.parent.video.vid_path) and url_as_path) or (self.parent.video.watched and show_watched) \
                or (self.parent.video.discarded and show_dismissed):
            if not self.parent.video.vid_path:
                self.logger.debug("Adding [NO FILE] overlay for: {} - {}".format(self.parent.video.title, self.__dict__))
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
