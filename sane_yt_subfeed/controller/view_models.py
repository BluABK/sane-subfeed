from PyQt5.QtCore import QThread

from sane_yt_subfeed.controller.listeners import GridViewListener, DatabaseListener


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

        self.database_listener = DatabaseListener()
        self.db_thread = QThread()
        self.db_thread.setObjectName('db_thread')
        self.grid_view_listener.moveToThread(self.db_thread)
        self.db_thread.start()

    def hide_video_item(self, index):
        del self.filtered_videos[index]
