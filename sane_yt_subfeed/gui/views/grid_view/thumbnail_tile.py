import os

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPainter, QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy

from sane_yt_subfeed.config_handler import read_config

OS_PATH = os.path.dirname(__file__)
OVERLAY_NEW_PATH = os.path.join(OS_PATH, '..', '..', 'icons', 'new_vid.png')
OVERLAY_MISSED_PATH = os.path.join(OS_PATH, '..', '..', 'icons', 'missed_vid.png')

class ThumbnailTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent

        margins = self.parent.layout.getContentsMargins()
        self.setFixedSize(self.parent.width() - margins[0] - margins[2], (self.parent.height()-4*margins[3]) * 0.6)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setPixmap(self, p):
        self.p = p

    def paintEvent(self, event):
        if self.p:
            painter = QPainter(self)
            # painter.drawPixmap(self.rect(), self.p)
            if read_config('Gui', 'keep_thumb_ar'):
                thumb = self.p.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(0, 0, thumb)

                if self.parent.video.missed:
                    overlay = QPixmap(OVERLAY_MISSED_PATH)
                    resize_ratio = min(thumb.width() * 0.7 / thumb.width(), thumb.height() * 0.3 / thumb.height())
                    new_size = QSize(thumb.width() * resize_ratio, thumb.height() * resize_ratio)
                    overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    point = QPoint(thumb.width() - overlay.width(), 0)
                    painter.drawPixmap(point, overlay)
                # elif self.parent.video.new:
                overlay = QPixmap(OVERLAY_NEW_PATH)
                resize_ratio = min(thumb.width()*0.7 / thumb.width(), thumb.height()*0.3 / thumb.height())
                new_size = QSize(thumb.width() * resize_ratio, thumb.height() * resize_ratio)
                overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                point = QPoint(thumb.width()-overlay.width(), 0)
                painter.drawPixmap(point, overlay)
            else:
                painter.drawPixmap(self.rect(), self.p)

                if self.parent.video.missed:
                    overlay = QPixmap(OVERLAY_MISSED_PATH)
                    resize_ratio = min(self.width() * 0.7 / self.width(), self.height() * 0.3 / self.height())
                    new_size = QSize(self.width() * resize_ratio, self.height() * resize_ratio)
                    overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    point = QPoint(self.width() - overlay.width(), 0)
                    painter.drawPixmap(point, overlay)
                elif self.parent.video.new:
                    overlay = QPixmap(OVERLAY_NEW_PATH)
                    resize_ratio = min(self.width()*0.7 / self.width(), self.height()*0.3 / self.height())
                    new_size = QSize(self.width() * resize_ratio, self.height() * resize_ratio)
                    overlay = overlay.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    point = QPoint(self.width()-overlay.width(), 0)
                    painter.drawPixmap(point, overlay)
    # def resizeEvent(self, *args, **kwargs):
    #     margins = self.parent.layout.getContentsMargins()
    #     self.setGeometry(margins[0], margins[1], self.parent.width() - 2 * margins[2],
    #                      (self.parent.height() - (4 * margins[1] + 4 * margins[3])) * 0.6)