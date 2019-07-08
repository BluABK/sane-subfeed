from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter
from PyQt5.QtWidgets import QScrollArea, QStyleOption, QStyle


class ConfigWindow(QScrollArea):

    def __init__(self, main_window):
        super(ConfigWindow, self).__init__()

        self.main_window = main_window
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
