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


class Controller:

    def __init__(self):
        super().__init__()
        self.vid_limit = 100
        # self.grid_view_listener = GridViewListener(self)
        # self.thread = QThread()
        # self.thread.start()
        # self.grid_view_listener.moveToThread(self.thread)

    def run(self):
        filter_dl = read_config('Gui', 'hide_downloaded')
        start_with_stored_videos = read_config('Debug', 'start_with_stored_videos')
        if start_with_stored_videos:
            subscription_feed = get_newest_stored_videos(self.vid_limit, filter_downloaded=filter_dl)
            if len(subscription_feed) < 1:
                print('Used start_with_stored_videos=True, but there where no stored videos found')
                print('Get new videos? (y)')
                user_response = input()
                if user_response == 'n':
                    exit(1)
                else:
                    subscription_feed = refresh_and_get_newest_videos(self.vid_limit, filter_downloaded=filter_dl)
        else:
            subscription_feed = refresh_and_get_newest_videos(self.vid_limit, filter_downloaded=filter_dl)

        model = MainModel([], subscription_feed, self.vid_limit)

        grid_view_x = read_config('Gui', 'grid_view_x')
        grid_view_y = read_config('Gui', 'grid_view_y')
        tile_pref_height = read_config('Gui', 'tile_pref_height')
        tile_pref_width = read_config('Gui', 'tile_pref_width')
        dimensions = [grid_view_x*tile_pref_width, grid_view_y*tile_pref_height]

        app = QApplication(sys.argv)
        window = MainWindow(model, dimensions=dimensions)
        window.show()
        app.exec_()
