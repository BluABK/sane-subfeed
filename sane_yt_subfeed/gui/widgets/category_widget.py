from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget

from sane_yt_subfeed import create_logger

AUTO_COLORS = ['#FFD700', '#DC143C', '#ADFF2F', '#1E90FF', '#EE82EE', '#FFFFFF', '#000000', '#9932CC']
AUTO_COLOR_COUNT = 0


class CategoryWidget(QWidget):
    def __init__(self, parent, name, color=None, enabled=True, icon=None, primary=False, *args, **kwargs):
        super(CategoryWidget, self).__init__(parent, *args, **kwargs)
        self.logger = create_logger(__name__)
        self.root = parent.root
        self.parent = parent

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

        self.logger.info("Created category widget: {} (color: {})".format(self.name, self.color.name(QColor.HexRgb)))
