from bs4 import BeautifulSoup

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import QLabel

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.utils import get_unicode_weight


class ElidedLabel(QLabel):

    def __init__(self, text, parent, font: QFont, cfg_lines_entry, cfg_elided_mod_entry):
        """
        Elided label (superclass).
        :param text:                    String to put on QLabel.
        :param parent:                  Parent ptr.
        :param cfg_lines_entry:         QFont font to use.
        """
        QLabel.__init__(self, text)
        self.parent = parent

        # Unescape HTML/XML codes, if any (usually happens with youtube.search() results)
        text = BeautifulSoup(text, "html.parser").text

        self.setFont(font)

        # Set label type independent config entries
        self.cfg_lines_entry: list = cfg_lines_entry
        self.cfg_elided_mod_entry: list = cfg_elided_mod_entry

        # Elided overwrites the original, so we need to keep a copy.
        self.original_text = text

        # Get font metrics/info.
        metrics = QFontMetrics(self.font())

        # Lines of text to show (determines height of title text item).
        lines = read_config(*self.cfg_lines_entry)

        # Offset the unicode because it has tall characters and its line spacing is thus larger than ASCII's.
        #
        # If set to 2 there will be 1px clearing beneath unicode,
        # but ASCII will show 1px of its supposedly cut-off next line.
        unicode_height_offset = read_config('GridView', 'tile_unicode_line_height_offset')

        # Set height equal to lines and add some newline spacing for unicode.
        self.setFixedHeight((metrics.height() * lines) + (unicode_height_offset * lines))

        # Set alignment and enable word wrapping so the text newlines instead of continuing OOB
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setWordWrap(True)

        # Finally, set the text string.
        self.setText(text, elided=True)

    def elide_text(self, p_str):
        """
        Elide text based on configurable values.
        :param p_str:   Text.
        :return:        Elided text.
        """
        # Get font metrics/info.
        metrics = QFontMetrics(self.font())

        # Get latest configurable values
        elided_modifier = read_config(*self.cfg_elided_mod_entry)
        lines = read_config(*self.cfg_lines_entry)
        unicode_weight_modifier = read_config('GridView', 'elided_text_unicode_weight_modifier')

        # Non-ASCII needs to be elided at an earlier width.
        elided_modifier -= get_unicode_weight(p_str, unicode_weight_modifier)

        # If the string text is wider than width, return an elided version of the string
        elided = metrics.elidedText(p_str, Qt.ElideRight, self.width() * elided_modifier * lines)
        return elided

    def setText(self, p_str, elided=False):
        """
        Override parent's function to explicitly set ellison, then call parent.
        :param p_str:   Text.
        :param elided:  Whether or not to set ellison.
        """
        self.original_text = p_str
        if elided:
            # FIXME: When called outside of init the width changes drastically, thus causing earlier and earlier cutoff.
            # Therefore elided=False by default, for now. Github issue #39
            p_str = self.elide_text(p_str)

        # Call parent to set modified text the standard way.
        super().setText(p_str)
