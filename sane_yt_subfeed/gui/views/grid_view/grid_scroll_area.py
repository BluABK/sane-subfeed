from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea


class GridScrollArea(QScrollArea):

    def __init__(self, parent):
        super(GridScrollArea, self).__init__(parent)

        self.parent = parent
        self.widget = None

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.resize(100, 100)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().setEnabled(False)

    def resizeEvent(self, QResizeEvent):
        self.widget.resize_event()
        super().resizeEvent(QResizeEvent)

    def set_view(self, widget):
        self.widget = widget
        self.setWidget(widget)
