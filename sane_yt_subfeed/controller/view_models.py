from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QProgressBar
from sqlalchemy import asc, desc, false, or_
from sqlalchemy.dialects import postgresql

from sane_yt_subfeed.config_handler import read_config, set_config
from sane_yt_subfeed.controller.listeners.database_listener import DatabaseListener
from sane_yt_subfeed.controller.listeners.download_handler import DownloadHandler
from sane_yt_subfeed.controller.listeners.listeners import GridViewListener, MainWindowListener, YtDirListener, \
    LISTENER_SIGNAL_NORMAL_REFRESH, ProgressBar
from sane_yt_subfeed.database.read_operations import get_newest_stored_videos, refresh_and_get_newest_videos, \
    get_best_playview_videos
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded


def remove_video(test_list, video):
    """
    Removes a video from list and returns the index it had
    :param test_list:
    :param video:
    :return:
    """
    for vid in test_list:
        if vid.video_id == video.video_id:
            index = test_list.index(vid)
            test_list.remove(vid)
            return index


def add_video(test_list, video, index):
    """
    Inserts a video into list at the given index
    :param test_list:
    :param video:
    :param index:
    :return:
    """
    test_list.insert(index, video)


class MainModel:
    status_bar_progress = None
    status_bar_thread = None
    status_bar_listener = None

    def __init__(self, videos, videos_limit, exceptions):
        super().__init__()
        self.logger = create_logger(__name__)
        self.exceptions = exceptions
        self.videos_limit = videos_limit
        self.playview_videos_limit = videos_limit
        self.videos = videos
        self.subfeed_videos = []
        self.playview_videos = []
        self.removed_videos = {'subfeed': {}, 'playview': {}}

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
            self.yt_dir_listener = None

    def get_exceptions(self):
        return self.exceptions

    def clear_exceptions(self):
        self.exceptions = []

    def determine_video_view(self, video):
        """
        Figures out which view/feed list the video belongs in.
        :param video:
        :return: list(key, the corresponding list the video belongs in).
        """
        if video in self.subfeed_videos:
            return ['subfeed', self.subfeed_videos]
        elif video in self.playview_videos:
            return ['playview', self.playview_videos]
        else:
            self.logger.error("Unable to determine which view video belongs to: {}".format(video.title))
            return None

    def determine_removed_video_view(self, video):
        """
        Figures out which view/feed list the removed video belongs in.
        :param video:
        :return: list(key, the corresponding list the video belongs in).
        """
        if video in self.removed_videos['subfeed']:
            return ['subfeed', self.subfeed_videos]
        elif video in self.removed_videos['playview']:
            return ['playview', self.playview_videos]
        else:
            self.logger.error("Unable to determine which view removed video belongs to: {}".format(video.title))
            return None

    def hide_video_item(self, video):
        """
        Hides a video from view.
        :param video:
        :return:
        """
        match = self.determine_video_view(video)
        if match:
            key, video_list = match
            self.logger.debug("Hiding video item: {}".format(video.title))
            self.removed_videos[key].update({video: remove_video(video_list, video)})
        else:
            # Even if we were unable to determine the view we should still remove the video (using the old method)
            self.logger.warning("Using failover method to determine view for video: {}".format(video.title))
            index_subfeed = remove_video(self.subfeed_videos, video)
            if index_subfeed:
                self.logger.warning("Failover method determined view to be '{}' for video: {}".format('subfeed',
                                                                                                      video.title))
                self.removed_videos['subfeed'].update({video: index_subfeed})
                return

            index_playview = remove_video(self.playview_videos, video)
            if index_playview:
                self.logger.warning("Failover method determined view to be '{}' for video: {}".format('playview',
                                                                                                      video.title))
                self.removed_videos['playview'].update({video: index_playview})
                return

            # All methods of determination has failed us
            self.logger.critical("ALL METHODS FAILED for determining which view video belongs to: {}".format(
                video.title))

    def unhide_video_item(self, video):
        """
        Shows a video previously hidden from view.
        :param video:
        :return:
        """
        match = self.determine_removed_video_view(video)
        if match:
            key, video_list = match
            self.logger.debug("Unhiding video item: {}".format(video.title))
            add_video(video_list, video, self.removed_videos[key][video])
            self.removed_videos[key].pop(video)

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

            self.subfeed_videos = get_newest_stored_videos(self.videos_limit, filters=update_filter)
            self.grid_view_listener.hiddenVideosChanged.emit()
        else:
            self.videos = get_newest_stored_videos(self.videos_limit, filtered)

    def remote_update_videos(self, filtered=True, refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
        self.logger.info("Reloading and getting newest videos from YouTube")

        if filtered:
            show_downloaded = not read_config('SubFeed', 'show_downloaded')
            show_dismissed = not read_config('GridView', 'show_dismissed')
            self.subfeed_videos = refresh_and_get_newest_videos(self.videos_limit,
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

    def db_update_play_view_videos(self):

        update_filter = self.config_get_filter_playback_view()
        update_sort = self.config_get_sort_playback_view()
        self.playview_videos = get_best_playview_videos(self.playview_videos_limit, filters=update_filter,
                                                        sort_method=update_sort)
        self.grid_view_listener.downloadedVideosChanged.emit()

    def update_thumbnails(self):
        videos = []
        videos.extend(self.playview_videos)
        videos.extend(self.subfeed_videos)
        self.logger.info("Updating thumbnails for downloaded and filtered videos")
        download_thumbnails_threaded(videos)
        UpdateVideosThread(videos, update_existing=True).start()

    @staticmethod
    def config_get_filter_playback_view():
        """
        Applies a filter to the PlaybackGridView Videos list.
        :return:
        """
        show_watched = read_config('GridView', 'show_watched')
        show_dismissed = read_config('GridView', 'show_dismissed')
        update_filter = (Video.downloaded,)
        if not show_watched:
            update_filter += (or_(Video.watched == false(), Video.watched == None),)
        if not show_dismissed:
            update_filter += (~Video.discarded,)
        return update_filter

    def config_get_sort_playback_view(self):
        """
        Applies a sort-by rule to the PlaybackGridView videos list.

        update_sort is a tuple of priority sort categories, first element is highest, last is lowest.
        update_sort += operations requires at least two items on rhs.
        :return:
        """
        sort_by_ascending_date = read_config('PlaySort', 'ascending_date')
        sort_by_channel = read_config('PlaySort', 'by_channel')
        self.logger.info("Sorting PlaybackGridView Videos: date = {} | channel = {}".format(sort_by_ascending_date,
                                                                                            sort_by_channel))
        update_sort = (asc(Video.watch_prio),)
        # Sort-by ascending date
        if sort_by_ascending_date:
            update_sort += (asc(Video.date_downloaded), asc(Video.date_published))
        # Sort-by channel name (implied by default: then descending date)
        if sort_by_channel:
            update_sort += (desc(Video.channel_title),)
        # Sort-by channel name then ascending date  # FIXME: Implement handling both sorts toggled
        if sort_by_channel and sort_by_ascending_date:
            # update_sort += (asc(Video.channel_title),)
            self.logger.debug5("By-Channel|By-date update_sort: {}".format(str(update_sort)))
            for t in update_sort:
                self.logger.debug5(t.compile(dialect=postgresql.dialect()))

            # FIXME: workaround for not handling both: disable channel sort if both toggled, and run date sort
            set_config('PlaySort', 'by_channel', format(not read_config('PlaySort', 'by_channel')))
            sort_by_channel = read_config('PlaySort', 'by_channel')
            update_sort += (asc(Video.date_downloaded), asc(Video.date_published))
        # DEFAULT: Sort-by descending date
        else:
            update_sort += (desc(Video.date_downloaded), desc(Video.date_published))

        self.logger.info("Sorted PlaybackGridView Videos: date = {} | channel = {}".format(sort_by_ascending_date,
                                                                                           sort_by_channel))
        return update_sort
