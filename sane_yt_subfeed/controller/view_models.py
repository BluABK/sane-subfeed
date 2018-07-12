from PyQt5.QtCore import QThread

# FIXME: imp*
from sane_yt_subfeed.controller.listeners import *
from sane_yt_subfeed.controller.test import MainWindowListener


class MainModel:

    def __init__(self, videos, filtered_videos):
        super().__init__()
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

        self.m_window_listener = MWindowListener(self)
        self.m_w_thread = QThread()
        self.m_w_thread.setObjectName('m_w_thread')
        self.m_window_listener.moveToThread(self.m_w_thread)
        self.m_w_thread.start()

    def hide_video_item(self, index):
        del self.filtered_videos[index]
