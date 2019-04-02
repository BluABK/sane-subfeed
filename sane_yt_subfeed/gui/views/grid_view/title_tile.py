from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel

from sane_yt_subfeed.config_handler import read_config


class TitleTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent

        margins = self.parent.layout.getContentsMargins()
        self.setFixedSize(self.parent.width() - margins[0] - margins[2], (self.parent.height() - 4 * margins[3]) * 0.18)

        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        t_font = self.font()
        t_font.setWeight(QFont.DemiBold)
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setFixedPitch(True)
        t_font.setPixelSize(self.height() * read_config('GridView', 'title_tile_pixel_size'))
        self.setFont(t_font)

    def update_font(self):
        metrics = QFontMetrics(self.font())
        # If the string text is wider than width, return an elided version of the string
        elided_modifier = read_config('GridView', 'elided_text_modifier')  # old: 1.8, new: 2.0
        elided = metrics.elidedText(self.parent.video.title, Qt.ElideRight, self.width() * elided_modifier)
        self.setText(elided)
