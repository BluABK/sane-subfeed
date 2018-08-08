import math

from PyQt5 import sip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile
from sane_yt_subfeed.log_handler import create_logger


class GridView(QWidget):
    def __init__(self, parent, root, main_model: MainModel):
        super(GridView, self).__init__(parent=parent)
        self.logger = create_logger(__name__)
        self.setMinimumSize(0, 0)
        self.parent = parent
        self.root = root  # MainWindow
        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar
        self.buffer = 10
        self.bar_correction = 0
        self.main_model = main_model
        self.pref_tile_height = read_config('Gui', 'tile_pref_height')
        self.pref_tile_width = read_config('Gui', 'tile_pref_width')
        self.q_labels = {}
        self.grid = QGridLayout()
        self.items_x = read_config('Gui', 'grid_view_x')
        self.items_y = read_config('Gui', 'grid_view_y')

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.grid.setContentsMargins(5, 5, 0, 0)
        self.grid.setSpacing(2)
        self.grid.setAlignment(Qt.AlignTop)
        self.setLayout(self.grid)

        self.setAutoFillBackground(True)
        self.set_bgcolor()


    def videos_changed(self):
        self.logger.info('Updating tiles')
        self.update_grid()

    def resize_event(self):
        if self.items_x >= 1:
            margins = self.grid.getContentsMargins()
            update_grid = False
            while self.parent.width() > (
                    (self.items_x + 1) * self.pref_tile_width + margins[0] + margins[2] + self.buffer):
                self.items_x += 1
                update_grid = True
            while self.parent.width() <= self.items_x * self.pref_tile_width + margins[0] + margins[
                2] and self.items_x > 1:
                self.items_x -= 1
                update_grid = True
            if update_grid:
                self.update_grid()

    def update_grid(self):
        feed = self.get_feed()
        counter = 0
        video_counter = 0
        q_labels_keys_to_delete = set(self.q_labels)

        positions = [(i, j) for i in
                     range(max(math.ceil(len(feed) / max(self.items_x, 1)), 1))
                     for j in
                     range(self.items_x)]
        for position in positions:
            if counter >= len(feed):
                pass
            elif feed[counter].video_id in self.q_labels:
                self.grid.addWidget(self.q_labels[feed[counter].video_id], *position)
                q_labels_keys_to_delete.discard(feed[counter].video_id)
                # q_labels_keys_to_delete.remove(feed[counter].video_id)
                video_counter += 1
            else:
                video = feed[counter]
                lbl = self.new_tile(counter, video)
                self.grid.addWidget(lbl, *position)
                self.q_labels[video.video_id] = lbl
                video_counter += 1
            counter += 1

        for key in q_labels_keys_to_delete:
            widget = self.q_labels[key]
            self.grid.removeWidget(widget)
            sip.delete(widget)
            self.q_labels.pop(key)
        self.logger.debug(
            "Updated view: currently {} widgets and {} items_x".format(video_counter, self.items_x))
        self.resize_event()

    def set_bgcolor(self, color="default", darkmode=False):
        palette = self.palette()
        if darkmode:
            palette.setColor(self.backgroundRole(), Qt.black)
        else:
            palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
