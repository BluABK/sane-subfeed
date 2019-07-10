from PySide2.QtCore.Qt import Qt
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtWidgets import QScrollArea, QStyleOption, QStyle


class ConfigScrollArea(QScrollArea):

    def __init__(self, parent):
        super(ConfigScrollArea, self).__init__(parent=parent)

        self.sane_parent = parent
        self.widget = None
        self.setWidgetResizable(True)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.slider_lock = False

        # self.resize(100, 100)

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

    def set_view(self, widget):
        self.widget = widget
        self.setWidget(widget)
