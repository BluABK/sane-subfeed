import os
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap

from sane_yt_subfeed.absolute_paths import ICONS_PATH, RESOURCES_PATH
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.grid_view.thumbnail_tile import ThumbnailTile
from sane_yt_subfeed.log_handler import create_logger

OVERLAY_NO_FILE_PATH = os.path.join(ICONS_PATH, 'no_file.png')
OVERLAY_DISCARDED_PATH = os.path.join(ICONS_PATH, 'dismissed.png')
OVERLAY_WATCHED_PATH = os.path.join(ICONS_PATH, 'watched.png')
THUMBNAIL_NA_PATH = os.path.join(RESOURCES_PATH, 'thumbnail_na.png')


class PlaybackGridViewThumbnailTile(ThumbnailTile):

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
        url_as_path = read_config('Play', 'use_url_as_path')
        watched = read_config('GridView', 'show_watched') and self.parent.video.watched
        discarded = read_config('GridView', 'show_dismissed') and self.parent.video.discarded

        if ((not self.parent.video.vid_path) and not url_as_path) or watched or discarded:
            if not self.parent.video.vid_path:
                overlay = QPixmap(OVERLAY_NO_FILE_PATH)
            elif self.parent.video.watched:
                overlay = QPixmap(OVERLAY_WATCHED_PATH)
            else:
                overlay = QPixmap(OVERLAY_DISCARDED_PATH)

            overlay_h = read_config('Gui', 'tile_overlay_height_pct', literal_eval=True) / 100
            overlay_w = read_config('Gui', 'tile_overlay_width_pct', literal_eval=True) / 100
            resize_ratio = min(thumb.width() * overlay_w / thumb.width(),
                               thumb.height() * overlay_h / thumb.height())
            new_size = QSize(thumb.width() * resize_ratio, thumb.height() * resize_ratio)
            overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            point = QPoint(thumb.width() - overlay.width(), 0)
            painter.drawPixmap(point, overlay)
