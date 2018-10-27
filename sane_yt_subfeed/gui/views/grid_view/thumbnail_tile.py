import os

from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtGui import QPainter, QImage, QPixmap, QBrush, QColor, QPen, QFont
from PyQt5.QtWidgets import QLabel, QSizePolicy

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.log_handler import create_logger

OS_PATH = os.path.dirname(__file__)
OVERLAY_NEW_PATH = os.path.join(OS_PATH, '..', '..', 'icons', 'new_vid.png')
OVERLAY_MISSED_PATH = os.path.join(OS_PATH, '..', '..', 'icons', 'missed_vid.png')
THUMBNAIL_NA_PATH = os.path.join(OS_PATH, '..', '..', '..', 'resources', 'thumbnail_na.png')


class ThumbnailTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.logger = create_logger(__name__ + ".ThumbnailTitle")

        margins = self.parent.layout.getContentsMargins()
        self.setFixedSize(self.parent.width() - margins[0] - margins[2], (self.parent.height() - 4 * margins[3]) * 0.6)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
                vid_info = "{} - {} [{}]".format(self.parent.video.channel_title, self.parent.video.title,
                                                 self.parent.video.url_video)
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
            pen = QPen(Qt.white)
            painter.setPen(pen)
            point = QPoint(thumb.width()*0.70, thumb.height()*0.85)
            rect = QRect(point, QSize(thumb.width()*0.28, thumb.height()*0.12))
            painter.fillRect(rect, QBrush(QColor(0, 0, 0, 180)))
            painter.drawText(rect, Qt.AlignCenter, format(self.parent.video.duration))

            # Overlay captions (if any) on thumbnail    # FIXME: Replace with something better like a small icon
            if self.parent.video.has_caption:
                pen = QPen(Qt.white)
                painter.setPen(pen)
                point = QPoint(thumb.width() * 0.03, thumb.height() * 0.85)
                rect = QRect(point, QSize(thumb.width() * 0.28, thumb.height() * 0.12))
                painter.fillRect(rect, QBrush(QColor(0, 0, 0, 180)))
                painter.drawText(rect, Qt.AlignCenter, "captions")

            if self.parent.video.definition == "sd":
                pen = QPen(Qt.red)
                painter.setPen(pen)
                point = QPoint(thumb.width() * 0.02, thumb.height() * 0.02)
                rect = QRect(point, QSize(thumb.width() * 0.16, thumb.height() * 0.20))
                painter.fillRect(rect, QBrush(QColor(0, 0, 0, 180)))
                self.logger.critical(painter.font())
                self.logger.critical(painter.fontInfo())
                self.logger.critical(painter)
                enlarged_font = QFont(painter.font())
                enlarged_font.setPointSize(14)
                painter.setFont(enlarged_font)
                painter.drawText(rect, Qt.AlignCenter, "SD")

            self.add_overlay(painter, thumb)

    def add_overlay(self, painter, thumb):
        """
        Add an overlay on top of the thumbnail
        :param painter:
        :param thumb:
        :return:
        """
        pass
