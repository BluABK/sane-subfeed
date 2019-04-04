from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.config_view.config_item_types import TILE_TITLE_FONT_WEIGHTS_MAP
from sane_yt_subfeed.utils import get_unicode_weight


class TitleTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent
        # Elided overwrites the original, so we need to keep a copy
        self.original_text = text

        self.setMaximumHeight(self.parent.height() * read_config('GridView', 'title_tile_max_height_modifier'))

        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.update_font()

    def update_font(self):
        t_font = self.font()
        t_font.setWeight(TILE_TITLE_FONT_WEIGHTS_MAP[read_config('GridView', 'title_tile_font_weight')])
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setFixedPitch(True)
        t_font.setPixelSize(self.height() * read_config('GridView', 'title_tile_pixel_size_modifier'))
        self.setFont(t_font)

        metrics = QFontMetrics(self.font())
        # If the string text is wider than width, return an elided version of the string
        elided_modifier = read_config('GridView', 'elided_text_modifier_title')  # old: 1.8, new: 2.0

        unicode_weight_modifier = read_config('GridView', 'elided_text_unicode_weight_modifier')

        # Non-ASCII needs to be elided at an earlier width.
        elided_modifier -= get_unicode_weight(self.original_text, unicode_weight_modifier)

        elided = metrics.elidedText(self.original_text, Qt.ElideRight, self.width() * elided_modifier)
        self.setText(elided)
