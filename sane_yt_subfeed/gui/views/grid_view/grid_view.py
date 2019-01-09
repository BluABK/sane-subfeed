import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.view_models import MainModel
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
        if root.bgcolor:
            self.set_bgcolor(root.bgcolor)

        # self.main_model.grid_view_listener.redrawVideos.connect(self.redraw_videos)

    def redraw_video(self, video):
        """
        Sets a video tile using their current properties.
        :param video:
        :return:
        """
        if video.video_id in self.q_labels.keys():
            self.logger.info("Redrawing video: {}".format(video))
            self.q_labels[video.video_id].set_video(video)
        else:
            self.logger.error("Was told to redraw video that isn't in q_labels.keys: {}".format(video))

    def redraw_videos(self, videos: list):
        """
        Sets all the video tiles using their current properties.
        :param videos:
        :return:
        """
        for video in videos:
            self.redraw_video(video)

    def repaint_video(self, video):
        """
        Sets pixmap on a video thumbnail tile using their current properties.
        :param video:
        :return:
        """
        if video.video_id in self.q_labels.keys():
            self.logger.info("Repainting video: {}".format(video))
            self.q_labels[video.video_id].set_thumbnail_pixmap(video.thumbnail_path)

    def repaint_videos(self, videos: list):
        """
        Sets pixmap on all video thumbnail tiles using their current properties.
        :param videos:
        :return:
        """
        for video in videos:
            self.repaint_video(video)

    def videos_changed(self):
        """
        Actions to be taken when video list detects a change.
        :return:
        """
        self.logger.info('Updating tiles (Videos change detected)')
        self.update_grid()

    def resize_event(self):
        """
        Handling of window being resized.
        :return:
        """
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

    def get_feed(self):
        """
        Retrieves the list of videos in a feed.
        Override in inheritance.
        :return: list
        """
        pass

    def update_grid(self):
        """
        Update/Redraw the GridView feed with a list of videos.
        :return:
        """
        feed: list = self.get_feed()
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
            # Add every existing video as a feed widget and remove it from the deletion list.
            elif feed[counter].video_id in self.q_labels:
                # self.logger.debug3("Inserting item in grid coord [{},{}]: {}".format(*position, feed[counter]))
                self.grid.addWidget(self.q_labels[feed[counter].video_id], *position)
                q_labels_keys_to_delete.discard(feed[counter].video_id)
                video_counter += 1
            else:
                # Add new video feed widgets
                video = feed[counter]
                # self.logger.debug3("Inserting *NEW* item in grid coord [{},{}]: {}".format(*position, video))
                lbl = self.new_tile(counter, video)
                self.grid.addWidget(lbl, *position)
                self.q_labels[video.video_id] = lbl
                video_counter += 1
            counter += 1

        # Delete any orphaned items remaining in the deletion list.
        for key in q_labels_keys_to_delete:
            # self.logger.debug3("Deleting orphaned grid video: {}".format(self.q_labels[key].video))
            self.grid.removeWidget(self.q_labels[key])
            self.q_labels[key].deleteLater()
            del self.q_labels[key]
        self.logger.debug("Updated view: currently {} widgets and {} items_x".format(video_counter, self.items_x))
        self.resize_event()

    def set_bgcolor(self, color):
        """
        Sets a background color based on a hexadecimal string.
        :param color:
        :return:
        """
        palette = self.palette()
        bgcolor = QColor(color)
        palette.setColor(self.backgroundRole(), bgcolor)
        self.setPalette(palette)
