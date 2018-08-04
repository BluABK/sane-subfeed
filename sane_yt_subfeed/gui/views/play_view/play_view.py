import os
import subprocess
import timeit

from PyQt5 import sip

from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView
from sane_yt_subfeed.gui.views.play_view.play_tile import PlayTile
from sane_yt_subfeed.log_handler import create_logger


class PlayView(GridView):

    def __init__(self, parent, main_model: MainModel, clipboard, status_bar):
        super().__init__(parent, main_model, clipboard, status_bar)

    def init_ui(self):
        self.logger = create_logger("PlayView")
        self.logger.info("Initializing UI")

        self.main_model.grid_view_listener.downloadedVideosChanged.connect(self.downloaded_videos_changed)

        self.update_grid()

    def get_feed(self):
        subscription_feed = self.main_model.downloaded_videos
        return subscription_feed

    def downloaded_videos_changed(self):
        self.logger.info('PlayView: Updating tiles')
        for q_label, video in zip(self.q_labels, self.main_model.downloaded_videos):
            q_label.set_video(video)


    def update_grid(self):
        feed = self.get_feed()
        counter = 0
        positions = [(i, j) for i in range(self.items_y) for j in range(self.items_x)]
        for position in positions:

            if counter < len(self.q_labels):
                self.grid.addWidget(self.q_labels[counter], *position)
            else:
                if counter >= len(feed):
                    vid_item = VideoD(None)
                    lbl = PlayTile(self, vid_item, counter, self.clipboard, self.status_bar)
                else:
                    lbl = PlayTile(self, feed[counter], counter, self.clipboard, self.status_bar)
                self.grid.addWidget(lbl, *position)
                self.q_labels.append(lbl)
            counter += 1
        if len(positions) < len(self.q_labels):
            widgets_to_delete = self.q_labels[len(positions):]
            self.q_labels = self.q_labels[:len(positions)]
            for widget in widgets_to_delete:
                self.grid.removeWidget(widget)
                sip.delete(widget)
        self.resizeEvent('')

