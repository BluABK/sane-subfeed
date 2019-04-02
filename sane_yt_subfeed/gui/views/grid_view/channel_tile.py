from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel

from sane_yt_subfeed.config_handler import read_config


class ChannelTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent

        margins = self.parent.layout.getContentsMargins()
        fixed_size_modifier = 0.07  # was 0.07
        self.setFixedSize(self.parent.width() - margins[0] - margins[2], (self.parent.height() - 4 * margins[3]) * fixed_size_modifier)

        t_font = self.font()
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setPixelSize(self.height())
        self.setFont(t_font)

    def update_font(self):
        metrics = QFontMetrics(self.font())
        # If the string text is wider than width, return an elided version of the string
        elided_modifier = read_config('GridView', 'elided_text_modifier_channel')
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width() * elided_modifier)
        self.setText(elided)
