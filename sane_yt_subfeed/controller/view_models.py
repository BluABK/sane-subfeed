from PyQt5.QtCore import QThread

# FIXME: imp*
from sane_yt_subfeed.controller.listeners import *
from sane_yt_subfeed.database.read_operations import get_newest_stored_videos, refresh_and_get_newest_videos
from sane_yt_subfeed.log_handler import create_logger


class MainModel:
    status_bar_progress = None
    status_bar_thread = None
    status_bar_listener = None

    def __init__(self, videos, filtered_videos, videos_limit):
        super().__init__()
        self.logger = create_logger('MainModel')
        self.videos_limit = videos_limit
        self.videos = videos
        self.filtered_videos = filtered_videos

        self.logger.info("Creating listeners and threads")
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
        self.logger.debug("Hiding video item: {}".format(index))
        del self.filtered_videos[index]
        regrab_percentage = read_config('Model', 'regrab_percentage')
        loaded_videos = read_config('Model', 'loaded_videos')
        self.videos_limit = loaded_videos
        if len(self.filtered_videos) <= int(regrab_percentage*loaded_videos):
            self.db_update_videos()
            # FIXME: only does filtered videos
            self.logger.warning('Reduced view models filtered_videos to /2, requesting new videos from db')

    def db_update_videos(self, filtered=True):
        self.logger.info("Getting newest stored videos from DB")
        # FIXME: only does filtered videos
        if filtered:
            self.filtered_videos = get_newest_stored_videos(self.videos_limit, filtered)
            self.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.videos = get_newest_stored_videos(self.videos_limit, filtered)

    def remote_update_videos(self, filtered=True, refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
        self.logger.info("Reloading and getting newest videos from YouTube")
        # FIXME: only does filtered videos
        if filtered:
            self.filtered_videos = refresh_and_get_newest_videos(self.videos_limit, filtered, self.status_bar_listener,
                                                                 refresh_type=refresh_type)
            self.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.videos = refresh_and_get_newest_videos(self.videos_limit, filtered, self.status_bar_listener,
                                                        refresh_type=refresh_type)

    def new_status_bar_progress(self, parent):
        self.status_bar_progress = QProgressBar(parent=parent)
        self.status_bar_listener = ProgressBar(self, self.status_bar_progress)
        self.status_bar_thread = QThread()
        self.status_bar_thread.setObjectName('status_bar_thread')
        self.status_bar_listener.moveToThread(self.status_bar_thread)
        self.status_bar_thread.start()
        return self.status_bar_progress
