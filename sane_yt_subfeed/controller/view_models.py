from PyQt5.QtCore import QThread

from sane_yt_subfeed.controller.listeners import GridViewListener, DatabaseListener


class MainModel:

    def __init__(self, videos, grid, filtered_grid):
        super().__init__()
        self.videos = videos
        self.grid = grid
        self.filtered_grid = filtered_grid

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

    def hide_grid_view_item(self, video, x, y):
        print('{}{}{}'.format(video, x, y))