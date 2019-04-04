from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.utils import get_unicode_weight


class DateTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent
        # Elided overwrites the original, so we need to keep a copy
        self.original_text = text

        self.setMaximumHeight(self.parent.height() * read_config('GridView', 'date_tile_max_height_modifier'))

        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        t_font = self.font()
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setPixelSize(self.height() * read_config('GridView', 'date_tile_pixel_size_modifier'))
        self.setFont(t_font)

        self.setText(text)

    def elide_text(self, p_str):
        metrics = QFontMetrics(self.font())
        # If the string text is wider than width, return an elided version of the string
        elided_modifier = read_config('GridView', 'elided_text_modifier_date')
        unicode_weight_modifier = read_config('GridView', 'elided_text_unicode_weight_modifier')

        # Non-ASCII needs to be elided at an earlier width.
        elided_modifier -= get_unicode_weight(p_str, unicode_weight_modifier)

        elided = metrics.elidedText(p_str, Qt.ElideRight, self.width() * elided_modifier)

        return elided

    def setText(self, p_str, elided=True):
        self.original_text = p_str
        if elided:
            p_str = self.elide_text(p_str)

        super().setText(p_str)
