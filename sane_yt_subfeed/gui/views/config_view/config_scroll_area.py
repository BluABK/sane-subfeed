from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea


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

    def set_view(self, widget):
        self.widget = widget
        self.setWidget(widget)
