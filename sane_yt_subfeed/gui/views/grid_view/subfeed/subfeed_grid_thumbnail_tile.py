from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap

from sane_yt_subfeed.absolute_paths import OVERLAY_DOWNLOADED_PATH, OVERLAY_WATCHED_PATH, OVERLAY_DISCARDED_PATH, \
    OVERLAY_MISSED_PATH, OVERLAY_NEW_PATH
from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.gui.views.grid_view.thumbnail_tile import ThumbnailTile
from sane_yt_subfeed.handlers.log_handler import create_logger


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

            overlay_h = read_config('Gui', 'tile_overlay_height_pct', literal_eval=True) / 100
            overlay_w = read_config('Gui', 'tile_overlay_width_pct', literal_eval=True) / 100
            resize_ratio = min(thumb.width() * overlay_w / thumb.width(),
                               thumb.height() * overlay_h / thumb.height())
            new_size = QSize(thumb.width() * resize_ratio, thumb.height() * resize_ratio)
            overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            point = QPoint(thumb.width() - overlay.width(), 0)
            painter.drawPixmap(point, overlay)
