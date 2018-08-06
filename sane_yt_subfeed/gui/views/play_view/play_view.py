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

    def __init__(self, parent, root, main_model: MainModel):
        super().__init__(parent, root, main_model)

    def init_ui(self):
        self.logger = create_logger(__name__ + ".PlayView")
        self.logger.info("Initializing UI")

        self.main_model.grid_view_listener.downloadedVideosChanged.connect(self.downloaded_videos_changed)

        self.update_grid()

    def get_feed(self):
        subscription_feed = self.main_model.downloaded_videos
        return subscription_feed

    def downloaded_videos_changed(self):
        self.logger.info('Updating tiles')
        self.update_grid()
        for q_label, video in zip(self.q_labels, self.main_model.downloaded_videos):
            q_label.set_video(video)

    def new_tile(self, counter, video):
        return PlayTile(self, video, counter, self.clipboard, self.status_bar)
