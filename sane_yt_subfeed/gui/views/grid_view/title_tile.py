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

        # Elided overwrites the original, so we need to keep a copy.
        self.original_text = text

        # Get font metrics/info.
        metrics = QFontMetrics(self.font())

        # Set up font.
        t_font: QFont = self.font()
        t_font.setWeight(TILE_TITLE_FONT_WEIGHTS_MAP[read_config('GridView', 'title_tile_font_weight')])
        t_font.setStyleHint(QFont.Helvetica)  # FIXME: Make font configurable
        t_font.setFixedPitch(True)

        # Lines of text to show (determines height of title text item).
        lines = read_config('GridView', 'tile_title_lines')

        # Offset the unicode because it has tall characters and its line spacing is thus larger than ASCII's.
        #
        # If set to 2 there will be 1px clearing beneath unicode,
        # but ASCII will show 1px of its supposedly cut-off next line.
        unicode_height_offset = read_config('GridView', 'tile_unicode_line_height_offset')  # = 1.99

        # Set height equal to lines and add some newline spacing for unicode.
        self.setFixedHeight((metrics.height() * lines) + (unicode_height_offset * lines))

        # Set alignment and enable word wrapping so the text newlines instead of continuing OOB.
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setWordWrap(True)

        # Set own font to the new modified one.
        self.setFont(t_font)

        # Finally, set the text string.
        self.setText(text)

    def elide_text(self, p_str):
        """
        Elide text based on configurable values.
        :param p_str:   Text.
        :return:        Elided text.
        """
        # Get font metrics/info.
        metrics = QFontMetrics(self.font())

        # Get latest configurable values
        elided_modifier = read_config('GridView', 'elided_text_modifier_title')
        lines = read_config('GridView', 'tile_title_lines')
        unicode_weight_modifier = read_config('GridView', 'elided_text_unicode_weight_modifier')

        # Non-ASCII needs to be elided at an earlier width.
        elided_modifier -= get_unicode_weight(p_str, unicode_weight_modifier)

        # If the string text is wider than width, return an elided version of the string
        elided = metrics.elidedText(p_str, Qt.ElideRight, self.width() * elided_modifier * lines)

        return elided

    def setText(self, p_str, elided=True):
        """
        Override parent's function to explicitly set ellison, then call parent.
        :param p_str:   Text.
        :param elided:  Whether or not to set ellison.
        """
        self.original_text = p_str
        if elided:
            p_str = self.elide_text(p_str)

        # Call parent to set modified text the standard way.
        super().setText(p_str)
