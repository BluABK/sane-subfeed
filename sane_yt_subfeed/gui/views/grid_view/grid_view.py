from PyQt5.QtWidgets import QWidget, QGridLayout

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.views.grid_view.video_tile import VideoTile
from sane_yt_subfeed.log_handler import logger


class GridView(QWidget):
    q_labels = []
    items_x = None
    items_y = None
    main_model = None

    def __init__(self, parent, main_model: MainModel, clipboard, status_bar):
        super(GridView, self).__init__(parent)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.main_model = main_model
        self.pref_tile_height = read_config('Gui', 'tile_pref_height')
        self.pref_tile_width = read_config('Gui', 'tile_pref_width')
        self.resize_enabled = read_config('Gui', 'enable_grid_resize')

        self.grid = QGridLayout()
        self.init_ui()

    def init_ui(self):
        logger.info("Initializing GridView UI")

        self.main_model.grid_view_listener.hiddenVideosChanged.connect(self.videos_changed)

        self.grid.setContentsMargins(5, 5, 5, 5)
        self.grid.setSpacing(0)
        self.setLayout(self.grid)

        self.items_x = read_config('Gui', 'grid_view_x')
        self.items_y = read_config('Gui', 'grid_view_y')

        subscription_feed = self.main_model.filtered_videos

        counter = 0
        positions = [(i, j) for i in range(self.items_y) for j in range(self.items_x)]
        for position in positions:
            if counter >= len(positions):
                break
            lbl = VideoTile(self, subscription_feed[counter], counter, self.clipboard, self.status_bar)

            self.q_labels.append(lbl)
            self.grid.addWidget(lbl, *position, 1, 1)
            counter += 1

    def videos_changed(self):
        logger.info('GridView: Updating tiles')
        for q_label, video in zip(self.q_labels, self.main_model.filtered_videos):
            q_label.set_video(video)

    def resizeEvent(self, QResizeEvent):
        if self.resize_enabled:
            if self.width() > self.items_x*self.pref_tile_width*1.2:
                self.items_x += 1
                self.update_grid()
            elif self.width() < self.items_x*self.pref_tile_width*0.8:
                self.items_x -= 1
                self.update_grid()
            elif self.height() > self.items_y*self.pref_tile_height*1.2:
                self.items_y += 1
                self.update_grid()
            elif self.height() < self.items_y*self.pref_tile_height*0.8:
                self.items_y -= 1
                self.update_grid()

    def update_grid(self):
        subscription_feed = self.main_model.filtered_videos
        counter = 0
        positions = [(i, j) for i in range(self.items_y) for j in range(self.items_x)]
        for position in positions:

            if counter < len(self.q_labels):
                self.grid.addWidget(self.q_labels[counter], *position, 1, 1)
            else:
                lbl = VideoTile(self, subscription_feed[counter], counter, self.clipboard, self.status_bar)
                self.grid.addWidget(lbl, *position, 1, 1)
                self.q_labels.append(lbl)
            counter += 1
        if len(positions) < len(self.q_labels):
            widgets_to_delete = self.q_labels[len(positions):]
            self.q_labels = self.q_labels[:len(positions)]
            for widget in widgets_to_delete:
                widget.deleteLater()
