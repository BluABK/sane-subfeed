import sys
import threading
import time

# FIXME: imp*
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication

# FIXME: imp*
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners import *
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.gui.main_window import MainWindow
from sane_yt_subfeed.database.read_operations import refresh_and_get_newest_videos, get_newest_stored_videos
from sane_yt_subfeed.log_handler import create_logger


class Controller:

    def __init__(self):
        super().__init__()
        self.logger = create_logger('Controller')
        # self.grid_view_listener = GridViewListener(self)
        # self.thread = QThread()
        # self.thread.start()
        # self.grid_view_listener.moveToThread(self.thread)

    def run(self):
        self.logger.info("Running Controller instance")
        vid_limit = read_config('Model', 'loaded_videos')

        filter_dl = read_config('Gui', 'hide_downloaded')
        start_with_stored_videos = read_config('Debug', 'start_with_stored_videos')
        if start_with_stored_videos:
            subscription_feed = get_newest_stored_videos(vid_limit, filter_downloaded=filter_dl)
            if len(subscription_feed) < 1:
                self.logger.warning('Used start_with_stored_videos=True, but there where no stored videos found')
                print('Used start_with_stored_videos=True, but there where no stored videos found')
                print('Get new videos? (y)')  # FIXME: Handle with GUI popup msg
                user_response = input()
                if user_response == 'n':
                    exit(1)
                else:
                    subscription_feed = refresh_and_get_newest_videos(vid_limit, filter_downloaded=filter_dl)
        else:
            subscription_feed = refresh_and_get_newest_videos(vid_limit, filter_downloaded=filter_dl)

        model = MainModel([], subscription_feed, vid_limit)
        self.logger.info("Created MainModel: len(subscription_feed) = {}, vid_limit = {}".format(len(subscription_feed), vid_limit))

        grid_view_x = read_config('Gui', 'grid_view_x')
        grid_view_y = read_config('Gui', 'grid_view_y')
        tile_pref_height = read_config('Gui', 'tile_pref_height')
        tile_pref_width = read_config('Gui', 'tile_pref_width')
        # FIXME: static buffer
        dimensions = [grid_view_x * tile_pref_width + 10, grid_view_y * tile_pref_height + 10]

        app = QApplication(sys.argv)
        self.logger.info("Created QApplication({})".format(sys.argv))
        window = MainWindow(model, dimensions=dimensions)
        self.logger.info("Created MainWindow({}, dimensions={})".format(model, dimensions))
        window.show()
        self.logger.info("Executing application")
        app.exec_()
        self.logger.info("*** APPLICATION EXIT ***\n")
