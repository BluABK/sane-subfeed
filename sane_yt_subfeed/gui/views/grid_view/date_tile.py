from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

from sane_yt_subfeed.config_handler import read_config


class DateTile(QLabel):

    def __init__(self, text, parent):
        QLabel.__init__(self, text)
        self.parent = parent

        margins = self.parent.layout.getContentsMargins()
        self.setFixedSize(self.parent.width() - margins[0] - margins[2], (self.parent.height() - 4 * margins[3]) * 0.07)

        t_font = self.font()
        t_font.setStyleHint(QFont.Helvetica)
        t_font.setPixelSize(self.height())
        self.setFont(t_font)

    def update_font(self):
        t_font = self.font()
        t_font.setPixelSize(self.height())
        self.setFont(t_font)

        metrics = QFontMetrics(self.font())
        elided_modifier = read_config('GridView', 'elided_text_modifier_date')
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width() * elided_modifier)
        self.setText(elided)
