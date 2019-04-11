from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFontMetrics, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.handlers.config_handler import read_config

AUTO_COLORS = ['#FFD700', '#DC143C', '#ADFF2F', '#1E90FF', '#EE82EE', '#FFFFFF', '#000000', '#9932CC']
AUTO_COLOR_COUNT = 0


class CategoryWidget(QWidget):
    def __init__(self, parent, name, category_listener, color=None, enabled=True, icon=None, *args, **kwargs):
        super(CategoryWidget, self).__init__(parent, *args, **kwargs)
        self.logger = create_logger(__name__)
        self.root = parent.root
        self.parent = parent

        self.category_listener = category_listener
        # self.category_listener.remove.connect()

        # self.id = category.id
        self.name = name

        if color:
            self.color = QColor(color)
        else:
            global AUTO_COLORS, AUTO_COLOR_COUNT
            self.color = QColor(AUTO_COLORS[AUTO_COLOR_COUNT])

            if AUTO_COLOR_COUNT >= len(AUTO_COLORS) - 1:
                AUTO_COLOR_COUNT = 0
            else:
                AUTO_COLOR_COUNT += 1

        self.enabled = enabled
        if icon:
            self.icon = icon
        else:
            self.icon = None
        self.primary_videos = []
        self.videos = []
        self.channels = []

        # Get font metrics/info.
        metrics = QFontMetrics(self.font())

        # Set up font.
        t_font: QFont = self.font()
        t_font.setStyleHint(QFont.Helvetica)  # FIXME: Make font configurable
        # t_font.setFixedPitch(True)

        # Offset the unicode because it has tall characters and its line spacing is thus larger than ASCII's.
        #
        # If set to 2 there will be 1px clearing beneath unicode,
        # but ASCII will show 1px of its supposedly cut-off next line.
        unicode_height_offset = read_config('GridView', 'tile_unicode_line_height_offset')  # = 1.99

        # Set height equal to lines (1) and add some newline spacing for unicode.
        lines = 2
        self.setFixedHeight((metrics.height() * lines) + (unicode_height_offset * lines))
        # self.setFixedHeight(read_config('Gui', 'category_label_height'))

        # Apply modified font.
        self.setFont(t_font)

        # Set up widget layout
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        # layout.setContentsMargins(0, 0, 0, 0)

        # Add items
        name_label = QLabel(self.name)
        # name_label.setBackgroundRole(self.color)
        text_color = '#000000'
        name_label.setStyleSheet("QLabel { background-color: " + self.get_color_hex() + "; " +
                                 "color: " + text_color + "; }")
        name_label.setAutoFillBackground(True)
        layout.addWidget(name_label)

        # Apply layout
        self.setLayout(layout)

        self.logger.info("Created category widget: {} (color: {})".format(self.name, self.get_color_hex()))

    def get_color_hex(self):
        return self.color.name(QColor.HexRgb)

    def remove(self):
        self.listener.remove(self)
        del self

    def rename(self, new_name):
        self.listener.rename(self, new_name)
