import os
import subprocess
import timeit

from sane_yt_subfeed.controller.view_models import MainModel, logger
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView


class PlayView(GridView):

    def __init__(self, parent, main_model: MainModel, clipboard, status_bar):
        super().__init__(parent, main_model, clipboard, status_bar)

    def init_ui(self):
        logger.info("Initializing PlayView UI")

        self.main_model.yt_dir_listener.downloadedVideosChanged.connect(self.downloaded_videos_changed)

        self.update_grid()

    def get_feed(self):
        subscription_feed = self.main_model.downloaded_videos
        return subscription_feed

    def downloaded_videos_changed(self):
        logger.info('PlayView: Updating tiles')
        for q_label, video in zip(self.q_labels, self.main_model.downloaded_videos):
            q_label.set_video(video)

    def play(self, file_path, player="mpc-hc64"):
        subprocess.Popen([player, file_path])


