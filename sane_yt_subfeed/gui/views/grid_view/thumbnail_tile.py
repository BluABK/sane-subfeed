import os
from PyQt5.QtGui import QPainter, QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy

OS_PATH = os.path.dirname(__file__)
OVERLAY_NEW_PATH = os.path.join(OS_PATH, '..', '..', 'icons', 'new_vid.png')

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
            painter.drawPixmap(self.rect(), self.p)
            if self.parent.video.new or self.parent.video.missed:
                overlay = QPixmap(OVERLAY_NEW_PATH)
                painter.drawPixmap(self.rect(), overlay)
            #painter.end()

    # def resizeEvent(self, *args, **kwargs):
    #     margins = self.parent.layout.getContentsMargins()
    #     self.setGeometry(margins[0], margins[1], self.parent.width() - 2 * margins[2],
    #                      (self.parent.height() - (4 * margins[1] + 4 * margins[3])) * 0.6)