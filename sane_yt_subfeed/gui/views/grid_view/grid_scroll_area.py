from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea

from sane_yt_subfeed.controller.static_controller_vars import PLAY_VIEW_ID, GRID_VIEW_ID
from sane_yt_subfeed.controller.view_models import MainModel


class GridScrollArea(QScrollArea):

    def __init__(self, parent, model: MainModel):
        super(GridScrollArea, self).__init__(parent)

        self.parent = parent
        self.model = model
        self.widget = None
        self.widget_id = None

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.resize(100, 100)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().setEnabled(False)
        self.verticalScrollBar().valueChanged.connect(self.slider_moved)
        self.current_v_max = self.verticalScrollBar().maximum()
        # self.model.grid_view_listener.hiddenVideosChanged.connect(self.unlock_slider_lock)

        self.slider_lock = False

    def slider_moved(self, value):
        if self.current_v_max == self.verticalScrollBar().maximum() and self.slider_lock:
            return
        if self.current_v_max != self.verticalScrollBar().maximum():
            self.current_v_max = self.verticalScrollBar().maximum()
            self.slider_lock = False
        if (not self.slider_lock) and value / self.verticalScrollBar().maximum() >= 1.0:
            if self.widget_id == GRID_VIEW_ID:
                self.model.grid_view_listener.scrollReachedEndGrid.emit()
            elif self.widget_id == PLAY_VIEW_ID:
                self.model.grid_view_listener.scrollReachedEndPlay.emit()
            self.slider_lock = True

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Home:
            self.verticalScrollBar().setValue(0)
        elif event.key() == Qt.Key_End:
            # FIXME: do something with auto reload so that this is not needed
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum() - 1)

    def resizeEvent(self, QResizeEvent):
        self.widget.resize_event()
        super().resizeEvent(QResizeEvent)

    def set_view(self, widget, widget_id):
        self.widget_id = widget_id
        self.widget = widget
        self.setWidget(widget)
