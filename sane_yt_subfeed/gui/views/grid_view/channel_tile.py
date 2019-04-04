from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel

from sane_yt_subfeed.config_handler import read_config


class ChannelTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent
        # Elided overwrites the original, so we need to keep a copy
        self.original_text = text

        self.setMaximumHeight(self.parent.height() * read_config('GridView', 'channel_title_tile_max_height_modifier'))

        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.update_font()

    def update_font(self):
        t_font = self.font()
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setPixelSize(self.height() * read_config('GridView', 'channel_title_tile_pixel_size_modifier'))
        self.setFont(t_font)

        metrics = QFontMetrics(self.font())
        # If the string text is wider than width, return an elided version of the string
        elided_modifier = read_config('GridView', 'elided_text_modifier_channel')
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width() * elided_modifier)
        self.setText(elided)
