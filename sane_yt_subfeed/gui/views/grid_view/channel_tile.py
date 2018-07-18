from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel


class ChannelTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent

        margins = self.parent.layout.getContentsMargins()
        self.setFixedSize(self.parent.width()-margins[0]-margins[2], (self.parent.height()-4*margins[3]) * 0.07)

        t_font = self.font()
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setPixelSize(self.height())
        self.setFont(t_font)

    # def resizeEvent(self, *args, **kwargs):
    #     margins = self.parent.layout.getContentsMargins()
    #     prev_h = (self.parent.height() - (4 * margins[1] + 4 * margins[3])) * 0.2 + (
    #                 self.parent.height() - (4 * margins[1] + 4 * margins[3])) * 0.6
    #     self.setGeometry(margins[0], prev_h + (3 * margins[1] + 2 * margins[3]), self.parent.width() - 2 * margins[2],
    #                      (self.parent.height() - (4 * margins[1] + 4 * margins[3])) * 0.09)
    #
    # def update_font(self):
    #     t_font = self.font()
    #     t_font.setPixelSize(self.height())
    #     self.setFont(t_font)