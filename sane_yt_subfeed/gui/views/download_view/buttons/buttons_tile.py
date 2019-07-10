from PySide2.QtCore.Qt import Qt
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtWidgets import QWidget, QHBoxLayout, QSizePolicy, QStyleOption, QStyle

from sane_yt_subfeed.gui.views.download_view.buttons.clear_finished import ClearFinishedDownloads


class ButtonsTile(QWidget):

    def __init__(self, parent):
        super(ButtonsTile, self).__init__(parent=parent)
        self.sane_parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.sane_layout = QHBoxLayout()
        self.sane_layout.setAlignment(Qt.AlignTop)

        self.clear_button = ClearFinishedDownloads(self, self.sane_parent)

        self.sane_layout.addWidget(self.clear_button)

        self.setLayout(self.sane_layout)

    def paintEvent(self, paint_event: QPaintEvent):
        """
        Override painEvent in order to support stylesheets.
        :param paint_event:
        :return:
        """
        style_option = QStyleOption()
        style_option.initFrom(self)
        painter = QPainter(self)
        style = self.style()
        style.drawPrimitive(QStyle.PE_Widget, style_option, painter, self)
