from PyQt5.QtCore import QThread

# FIXME: imp*
from sane_yt_subfeed.controller.listeners import *
from sane_yt_subfeed.database.read_operations import get_newest_stored_videos


class MainModel:

    def __init__(self, videos, filtered_videos, videos_limit):
        super().__init__()
        self.videos_limit = videos_limit
        self.videos = videos
        self.filtered_videos = filtered_videos

        self.grid_view_listener = GridViewListener(self)
        self.grid_thread = QThread()
        self.grid_thread.setObjectName('grid_thread')
        self.grid_view_listener.moveToThread(self.grid_thread)
        self.grid_thread.start()

        self.database_listener = DatabaseListener(self)
        self.db_thread = QThread()
        self.db_thread.setObjectName('db_thread')
        self.database_listener.moveToThread(self.db_thread)
        self.db_thread.start()

        self.main_window_listener = MainWindowListener(self)
        self.main_w_thread = QThread()
        self.main_w_thread.setObjectName('main_w_thread')
        self.main_window_listener.moveToThread(self.main_w_thread)
        self.main_w_thread.start()

    def hide_video_item(self, index):
        del self.filtered_videos[index]
        if len(self.filtered_videos) < self.videos_limit/2:
            self.db_update_videos()
            # FIXME: only does filtered videos
            logger.info('Reduced view models filtered_videos to /2, requesting new videos from db')

    def db_update_videos(self, filtered=True):
        if filtered:
            self.filtered_videos = get_newest_stored_videos(self.videos_limit, filtered)
            self.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.videos = get_newest_stored_videos(self.videos_limit, filtered)
