from sane_yt_subfeed.gui.views.grid_view.labels.elided_label import ElidedLabel
from sane_yt_subfeed.handlers.config_handler import read_config
from PyQt5.QtGui import QFont

CFG_LINES_ENTRY = ['GridView', 'tile_title_lines']
CFG_ELIDED_MOD_ENTRY = ['GridView', 'elided_text_modifier_title']


class TitleLabel(ElidedLabel):

    def __init__(self, text, parent):
        font = QFont()
        font.fromString(read_config("Fonts", "video_title_font", literal_eval=False))

        ElidedLabel.__init__(self, text, parent, font, CFG_LINES_ENTRY, CFG_ELIDED_MOD_ENTRY)
