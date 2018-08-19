import time

from PyQt5.QtCore import QThread
# FIXME: imp*
from PyQt5.QtWidgets import QProgressBar
from sqlalchemy import asc, desc

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners.database_listener import DatabaseListener
from sane_yt_subfeed.controller.listeners.download_handler import DownloadHandler
from sane_yt_subfeed.controller.listeners.listeners import GridViewListener, MainWindowListener, YtDirListener, \
    LISTENER_SIGNAL_NORMAL_REFRESH, ProgressBar
from sane_yt_subfeed.database.read_operations import get_newest_stored_videos, refresh_and_get_newest_videos, \
    get_best_downloaded_videos
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded


def remove_video(test_list, video):
    for vid in test_list:
        if vid.video_id == video.video_id:
            test_list.remove(vid)


class MainModel:
    status_bar_progress = None
    status_bar_thread = None
    status_bar_listener = None

    def __init__(self, videos, videos_limit):
        super().__init__()
        self.logger = create_logger(__name__)
        self.videos_limit = videos_limit
        self.downloaded_videos_limit = videos_limit
        self.videos = videos
        self.filtered_videos = []
        self.downloaded_videos = []

        self.download_progress_signals = []

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

        self.download_handler = DownloadHandler(self)
        self.download_thread = QThread()
        self.download_thread.setObjectName('download_thread')
        self.download_handler.moveToThread(self.download_thread)
        self.download_thread.start()

        if read_config("Play", "yt_file_path", literal_eval=False):
            self.yt_dir_listener = YtDirListener(self)
            self.yt_dir_thread = QThread()
            self.yt_dir_thread.setObjectName('yt_dir_thread')
            self.yt_dir_listener.moveToThread(self.yt_dir_thread)
            self.yt_dir_thread.start()
        else:
            self.logger.warning("No youtube file path provided, directory listener is disabled")

    def hide_video_item(self, video):
        self.logger.debug("Hiding video item: {}".format(video))
        remove_video(self.filtered_videos, video)
        remove_video(self.downloaded_videos, video)

    def hide_downloaded_video_item(self, video):
        remove_video(self.downloaded_videos, video)

    def db_update_videos(self, filtered=True):
        self.logger.info("Getting newest stored videos from DB")
        # FIXME: only does filtered videos
        if filtered:
            show_downloaded = read_config('SubFeed', 'show_downloaded')
            show_dismissed = read_config('GridView', 'show_dismissed')
            update_filter = ()
            if not show_downloaded:
                update_filter += (~Video.downloaded,)
            if not show_dismissed:
                update_filter += (~Video.discarded,)

            self.filtered_videos = get_newest_stored_videos(self.videos_limit, filters=update_filter)
            self.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.videos = get_newest_stored_videos(self.videos_limit, filtered)

    def remote_update_videos(self, filtered=True, refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
        self.logger.info("Reloading and getting newest videos from YouTube")

        if filtered:
            show_downloaded = not read_config('SubFeed', 'show_downloaded')
            show_dismissed = not read_config('GridView', 'show_dismissed')
            self.filtered_videos = refresh_and_get_newest_videos(self.videos_limit,
                                                                 progress_listener=self.status_bar_listener,
                                                                 refresh_type=refresh_type,
                                                                 filter_discarded=show_dismissed,
                                                                 filter_downloaded=show_downloaded)
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

    def db_update_downloaded_videos(self):

        update_filter = self.config_get_filter_downloaded()
        update_sort = self.config_get_sort_downloaded()
        self.downloaded_videos = get_best_downloaded_videos(self.downloaded_videos_limit, filters=update_filter,
                                                            sort_method=update_sort)
        self.grid_view_listener.downloadedVideosChanged.emit()

    def update_thumbnails(self):
        videos = []
        videos.extend(self.downloaded_videos)
        videos.extend(self.filtered_videos)
        self.logger.info("Updating thumbnails for downloaded and filtered videos")
        download_thumbnails_threaded(videos)
        UpdateVideosThread(videos, update_existing=True).start()

    def config_get_filter_downloaded(self):
        show_watched = read_config('GridView', 'show_watched')
        show_dismissed = read_config('GridView', 'show_dismissed')
        update_filter = (Video.downloaded,)
        if not show_watched:
            update_filter += (~Video.watched,)
        if not show_dismissed:
            update_filter += (~Video.discarded,)
        return update_filter

    def config_get_sort_downloaded(self):
        ascending_date = read_config('PlaySort', 'ascending_date')
        update_sort = (asc(Video.watch_prio),)
        if ascending_date:
            update_sort += (asc(Video.date_downloaded), asc(Video.date_published))
        else:
            update_sort += (desc(Video.date_downloaded), desc(Video.date_published))
        return update_sort

