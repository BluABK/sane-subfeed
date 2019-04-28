from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QColor, QPen, QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel

from sane_yt_subfeed.absolute_paths import THUMBNAIL_NA_PATH
from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.handlers.log_handler import create_logger


class ThumbnailTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.logger = create_logger(__name__ + ".ThumbnailTitle")

        margins = self.parent.layout.getContentsMargins()
        self.setFixedSize(self.parent.width() - margins[0] - margins[2], (self.parent.height() - 4 * margins[3]) * 0.6)

    def setPixmap(self, p):
        """
        Override setPixmap
        :param p:  <class 'PyQt5.QtGui.QPixmap'>: <PyQt5.QtGui.QPixmap object>
        :return:
        """
        # self.logger.debug("{}: {}".format(type(p), p))
        self.p = p

    def paintEvent(self, event):
        if self.p:
            if self.p.isNull():
                vid_info = "{}".format(self.parent.video)
                self.logger.warning("QPixmap self.p was NULL, replacing with 'Thumbnail N/A' image! Video: {}".format(
                    vid_info))
                self.p = QPixmap(THUMBNAIL_NA_PATH)

            painter = QPainter(self)

            if read_config('Gui', 'keep_thumb_ar'):
                thumb = self.p.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(0, 0, thumb)
            else:
                thumb = self
                painter.drawPixmap(thumb.rect(), thumb.p)

            # Overlay video duration on thumbnail
            font = QFont()
            font.fromString(read_config("Fonts", "video_thumbnail_overlay_font", literal_eval=False))

            pen = QPen(Qt.white)
            painter.setPen(pen)
            painter.setFont(font)

            duration_right_padding = 4
            duration_bottom_padding = 8

            point = QPoint(
                thumb.width() - duration_right_padding,
                thumb.height() - duration_bottom_padding
             )
            metrics = QFontMetrics(font)
            duration_string = format(self.parent.video.duration)
            # Find out the width of the text
            text_width = metrics.width(duration_string)
            # Work out the max height the text can be
            text_height = metrics.descent() + metrics.ascent()
            # Add a padding of 8px (4px on left, 4px on right) for width
            rect_width = text_width + 8
            # Add a padding of 4px (2px on top, 2px on bottom) for height
            rect_height = text_height + 4
            # Create a rectangle
            # point starts at the bottom right so we need to use negative sizes
            # because we need to move closer to 0,0 again
            rect = QRect(point, QSize(-rect_width, -rect_height))
            painter.fillRect(rect, QBrush(QColor(0, 0, 0, 180)))
            painter.drawText(rect, Qt.AlignCenter, duration_string)

            # Overlay captions (if any) on thumbnail    # FIXME: Replace with something better like a small icon
            if self.parent.video.has_caption and read_config('GridView', 'show_has_captions'):
                pen = QPen(Qt.white)
                painter.setPen(pen)
                painter.setFont(font)

                captions_left_padding = 4
                captions_bottom_padding = 8

                point = QPoint(
                    captions_left_padding,
                    thumb.height() - captions_bottom_padding
                )
                metrics = QFontMetrics(font)
                text_width = metrics.width("captions")
                text_height = metrics.descent() + metrics.ascent()
                rect_width = text_width + 8
                rect_height = text_height + 4

                rect = QRect(point, QSize(rect_width, -rect_height))
                painter.fillRect(rect, QBrush(QColor(0, 0, 0, 180)))
                painter.drawText(rect, Qt.AlignCenter, "captions")

            if self.parent.video.definition == "sd" and read_config('GridView', 'show_sd_warning'):
                pen = QPen(Qt.red)
                painter.setPen(pen)
                painter.setFont(font)

                sd_left_padding = 4
                sd_top_padding = 4

                point = QPoint(
                    sd_left_padding,
                    sd_top_padding
                )
                metrics = QFontMetrics(font)
                text_width = metrics.width("SD")
                text_height = metrics.descent() + metrics.ascent()
                rect_width = text_width + 4
                rect_height = text_height + 4

                rect = QRect(point, QSize(rect_width, rect_height))
                painter.fillRect(rect, QBrush(QColor(0, 0, 0, 180)))
                painter.drawText(rect, Qt.AlignCenter, "SD")

            self.add_overlay(painter, thumb)

    def add_overlay(self, painter, thumb):
        """
        Add an overlay on top of the thumbnail
        :param painter:
        :param thumb:
        :return:
        """
        raise ValueError("Implement add_overlay in inherited class!")
