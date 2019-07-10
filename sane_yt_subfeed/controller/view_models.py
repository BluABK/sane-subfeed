from PySide2.QtCore import QThread
from PySide2.QtGui import QPalette, QColor
from PySide2.QtWidgets import QProgressBar
from sqlalchemy import asc, desc, false, or_
from sqlalchemy.dialects import postgresql

from sane_yt_subfeed.handlers.config_handler import read_config, set_config
from sane_yt_subfeed.controller.listeners.database.database_listener import DatabaseListener
from sane_yt_subfeed.controller.listeners.gui.main_window.main_window_listener import MainWindowListener
from sane_yt_subfeed.controller.listeners.gui.progress_bar.progress_bar_listener import ProgressBarListener
from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.controller.listeners.gui.views.grid_view.playback.playback_grid_view_listener import \
    PlaybackGridViewListener
from sane_yt_subfeed.controller.listeners.gui.views.grid_view.subfeed.subfeed_grid_view_listener import \
    SubfeedGridViewListener
from sane_yt_subfeed.controller.listeners.listeners import LISTENER_SIGNAL_NORMAL_REFRESH
from sane_yt_subfeed.controller.static_controller_vars import PLAYBACK_VIEW_ID, SUBFEED_VIEW_ID
from sane_yt_subfeed.controller.listeners.youtube_dir_listener.youtube_dir_listener import YoutubeDirListener
from sane_yt_subfeed.database.read_operations import get_db_videos_subfeed, refresh_and_get_newest_videos, \
    get_db_videos_playback
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.exceptions.sane_aborted_operation import SaneAbortedOperation
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded


def remove_video(videos_list, video):
    """
    Removes a video from list and returns the index it had
    :param videos_list:
    :param video:
    :return:
    """
    for vid in videos_list:
        if vid.video_id == video.video_id:
            index = videos_list.index(vid)
            videos_list.remove(vid)
            return index


def add_video(videos_list, video, index):
    """
    Inserts a video into list at the given index
    :param videos_list:
    :param video:
    :param index:
    :return:
    """
    videos_list.insert(index, video)


class MainModel:
    status_bar_progress = None
    status_bar_thread = None
    status_bar_listener = None

    def __init__(self, videos, videos_limit):
        super().__init__()
        self.logger = create_logger(__name__)
        self.videos_limit = videos_limit
        self.playview_videos_limit = videos_limit
        self.videos = videos
        self.subfeed_videos = []
        self.subfeed_videos_removed = {}
        self.playview_videos = []
        self.playview_videos_removed = {}

        self.download_progress_signals = []

        self.logger.info("Creating listeners and threads")
        self.playback_grid_view_listener = PlaybackGridViewListener(self)
        self.playback_grid_thread = QThread()
        self.playback_grid_thread.setObjectName('playback_grid_thread')
        self.playback_grid_view_listener.moveToThread(self.playback_grid_thread)
        self.playback_grid_thread.start()
        self.subfeed_grid_view_listener = SubfeedGridViewListener(self)
        self.subfeed_grid_thread = QThread()
        self.subfeed_grid_thread.setObjectName('subfeed_grid_thread')
        self.subfeed_grid_view_listener.moveToThread(self.subfeed_grid_thread)
        self.subfeed_grid_thread.start()

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

        self.download_handler = DownloadViewListener(self)
        self.download_thread = QThread()
        self.download_thread.setObjectName('download_thread')
        self.download_handler.moveToThread(self.download_thread)
        self.download_thread.start()

        if read_config("Play", "yt_file_path", literal_eval=False):
            self.yt_dir_listener = YoutubeDirListener(self)
            self.yt_dir_thread = QThread()
            self.yt_dir_thread.setObjectName('yt_dir_thread')
            self.yt_dir_listener.moveToThread(self.yt_dir_thread)
            self.yt_dir_thread.start()
        else:
            self.logger.warning("No youtube file path provided, directory listener is disabled")
            self.yt_dir_listener = None

    def hide_video_item(self, video, widget_id):
        """
        Hides the video from a View.
        :param widget_id: Identifier for which View called this function.
        :param video:
        :return:
        """
        if widget_id:
            self.logger.debug("Hiding video item: {}".format(video))
            if widget_id == SUBFEED_VIEW_ID:
                self.subfeed_videos_removed.update({video: remove_video(self.subfeed_videos, video)})
            elif widget_id == PLAYBACK_VIEW_ID:
                self.playview_videos_removed.update({video: remove_video(self.playview_videos, video)})
        else:
            self.logger.error("Unable to hide video item: widget_id was None!")

    def unhide_video_item(self, video, widget_id):
        """
        Shows a video previously hidden from view.
        :param widget_id: Identifier for which View called this function.
        :param video:
        :return:
        """
        if widget_id:
            self.logger.debug("Un-hiding video item: {}".format(video.title))
            if widget_id == SUBFEED_VIEW_ID:
                add_video(self.subfeed_videos, video, self.subfeed_videos_removed[video])
                self.subfeed_videos_removed.pop(video)
            elif widget_id == PLAYBACK_VIEW_ID:
                add_video(self.playview_videos, video, self.playview_videos_removed[video])
                self.playview_videos_removed.pop(video)
        else:
            self.logger.error("Unable to hide video item: widget_id was None!")

    def update_subfeed_videos_from_db(self, filtered=True):
        """
        Updates Subscription feed video list from DB.

        Updates the filter with values in model and calls static database (read operation)
        function which doesn't have direct access to the model object.
        :param filtered:
        :return:
        """
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

            self.subfeed_videos = get_db_videos_subfeed(self.videos_limit, filters=update_filter)
            self.subfeed_grid_view_listener.videosChanged.emit()
        else:
            self.videos = get_db_videos_subfeed(self.videos_limit, filtered)

    def update_subfeed_videos_from_remote(self, filtered=True, refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
        """
        Updates Subscription feed video list from a remote source (likely YouTube API).

        :param filtered: Whether to filter out certain videos based on set boolean attributes.
        :param refresh_type: A signal determining whether it is a Normal (int(0)) or Deep (int(1)) refresh.
                             This kwarg is not used here, but passed on to the refresh function.
        :return:
        """
        self.logger.info("Reloading and getting newest videos from YouTube")
        try:
            if filtered:
                show_downloaded = not read_config('SubFeed', 'show_downloaded')
                show_dismissed = not read_config('GridView', 'show_dismissed')
                self.subfeed_videos = refresh_and_get_newest_videos(self.videos_limit,
                                                                    progress_listener=self.status_bar_listener,
                                                                    refresh_type=refresh_type,
                                                                    filter_discarded=show_dismissed,
                                                                    filter_downloaded=show_downloaded)
                self.subfeed_grid_view_listener.videosChanged.emit()
            else:
                self.videos = refresh_and_get_newest_videos(self.videos_limit, filtered, self.status_bar_listener,
                                                            refresh_type=refresh_type)
        except SaneAbortedOperation as exc_sao:
            # FIXME: Send aborted operation signal back up to GUI
            self.logger.critical("A SaneAbortedOperation exc occurred while updating subfeed from remote! Exceptions:")
            for exc in exc_sao.exceptions:
                self.logger.exception(str(exc), exc_info=exc_sao)

    def update_playback_videos_from_db(self):
        """
        Update the PlaybackView video list from DB.

        Note: There's no remote update for PlaybackView like there is for SubfeedView.
        :return:
        """
        update_filter = self.filter_playback_view_videos()
        update_sort = self.sort_playback_view_videos()
        self.playview_videos = get_db_videos_playback(self.playview_videos_limit, filters=update_filter,
                                                      sort_method=update_sort)
        self.playback_grid_view_listener.videosChanged.emit()

    def create_progressbar_on_statusbar(self, parent):
        """
        Creates a QProgressBar and attaches it to the status bar.
        :param parent:
        :return:
        """
        self.status_bar_progress = QProgressBar(parent=parent)
        palette = QPalette(self.status_bar_progress.palette())
        palette.setColor(QPalette.Highlight, QColor(24, 68, 91).lighter(200))
        self.status_bar_progress.setPalette(palette)
        self.status_bar_listener = ProgressBarListener(self, self.status_bar_progress)
        self.status_bar_thread = QThread()
        self.status_bar_thread.setObjectName('status_bar_thread')
        self.status_bar_listener.moveToThread(self.status_bar_thread)
        self.status_bar_thread.start()

        return self.status_bar_progress

    def update_thumbnails(self):
        """
        Updates thumbnails for downloaded and filtered videos.
        :return:
        """
        videos = []
        videos.extend(self.playview_videos)
        videos.extend(self.subfeed_videos)
        self.logger.info("Updating thumbnails for downloaded and filtered videos")
        download_thumbnails_threaded(videos)
        UpdateVideosThread(videos, update_existing=True).start()

    @staticmethod
    def filter_playback_view_videos():
        """
        Applies filters to the PlaybackGridView Videos list based on config.
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

    def sort_playback_view_videos(self):
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
