from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel, QSizePolicy


class ThumbnailTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setPixmap(self, p):
        self.p = p

    def paintEvent(self, event):
        if self.p:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p)

    def resizeEvent(self, *args, **kwargs):
        margins = self.parent.layout.getContentsMargins()
        self.setGeometry(margins[0], margins[1], self.parent.width() - 2 * margins[2],
                         (self.parent.height() - (4 * margins[1] + 4 * margins[3])) * 0.6)