from sane_yt_subfeed.gui.views.grid_view.labels.elided_label import ElidedLabel
from sane_yt_subfeed.handlers.config_handler import read_config
from PySide2.QtGui import QFont

CFG_LINES_ENTRY = ['GridView', 'tile_date_lines']
CFG_ELIDED_MOD_ENTRY = ['GridView', 'elided_text_modifier_date']


class DateLabel(ElidedLabel):

    def __init__(self, text, parent):
        font = QFont()
        font.fromString(read_config("Fonts", "video_date_font", literal_eval=False))

        ElidedLabel.__init__(self, text, parent, font, CFG_LINES_ENTRY, CFG_ELIDED_MOD_ENTRY)
