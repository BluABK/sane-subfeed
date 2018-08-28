import os

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPainter, QImage, QPixmap
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
                self.logger.warning("QPixmap self.p was NULL, replacing with 'Thumbnail N/A' image!")
                self.p = QPixmap(THUMBNAIL_NA_PATH)

            painter = QPainter(self)

            if read_config('Gui', 'keep_thumb_ar'):
                thumb = self.p.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(0, 0, thumb)
            else:
                thumb = self
                painter.drawPixmap(thumb.rect(), thumb.p)

            self.add_overlay(painter, thumb)

    def add_overlay(self, painter, thumb):
        """
        Add an overlay on top of the thumbnail
        :param painter:
        :param thumb:
        :return:
        """
        pass
