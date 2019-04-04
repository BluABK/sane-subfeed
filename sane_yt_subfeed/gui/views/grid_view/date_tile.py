from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

from sane_yt_subfeed.config_handler import read_config


class DateTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent

        # Extract the left, top, right, and bottom margins used around the layout
        margins = self.parent.layout.getContentsMargins()
        fixed_size_modifier = 0.07
        self.setFixedSize(self.parent.width() - margins[0] - margins[2],
                          (self.parent.height() - 4 * margins[3]) * fixed_size_modifier)

        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.update_font()

    def update_font(self):
        t_font = self.font()
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setPixelSize(self.height() * read_config('GridView', 'date_tile_pixel_size_modifier'))
        self.setFont(t_font)

        metrics = QFontMetrics(self.font())
        # If the string text is wider than width, return an elided version of the string
        elided_modifier = read_config('GridView', 'elided_text_modifier_date')
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width() * elided_modifier)
        self.setText(elided)
