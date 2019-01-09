import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.detached_models.video_d import VIDEO_KIND_VOD, VIDEO_KIND_LIVE, \
    VIDEO_KIND_LIVE_SCHEDULED, VIDEO_KIND_PREMIERE
from sane_yt_subfeed.gui.views.grid_view.channel_tile import ChannelTile
from sane_yt_subfeed.gui.views.grid_view.date_tile import DateTile
from sane_yt_subfeed.gui.views.grid_view.title_tile import TitleTile
from sane_yt_subfeed.history_handler import update_plaintext_history
from sane_yt_subfeed.log_handler import logger
from sane_yt_subfeed.youtube.thumbnail_handler import resize_thumbnail


class VideoTile(QWidget):
    hotkey_ctrl_down = False

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        QWidget.__init__(self, parent=parent)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.video = video
        self.id = vid_id
        self.parent = parent
        self.root = parent.root  # MainWindow
        self.history = self.root.history

        self.pref_height = read_config('Gui', 'tile_pref_height')
        self.pref_width = read_config('Gui', 'tile_pref_width')
        self.setFixedSize(self.pref_width, self.pref_height)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 4)
        self.thumbnail_widget = self.init_thumbnail_tile()
        self.layout.addWidget(self.thumbnail_widget)

        self.title_widget = TitleTile(video.title, self)
        self.layout.addWidget(self.title_widget)
        self.channel_widget = ChannelTile(video.channel_title, self)
        self.layout.addWidget(self.channel_widget)

        self.date_widget = DateTile('', self)
        self.layout.addWidget(self.date_widget)

        self.setLayout(self.layout)

        self.set_video(video)

    def init_thumbnail_tile(self):
        raise ValueError("ThumbnailTile initialised from VideoTile, not subclass!")

    def set_thumbnail_pixmap(self, thumbnail_path):
        """
        Runs
        :return:
        """
        self.thumbnail_widget.setPixmap(QPixmap(thumbnail_path))
        self.update()

    def set_video(self, video):
        self.video = video
        self.set_tool_tip()
        self.title_widget.update_font()

        show_grab_method = read_config('Debug', 'show_grab_method')
        if show_grab_method:
            grab_method = ''
            grab_methods = video.grab_methods
            if len(grab_methods) > 0:
                grab_method = grab_methods[0]
                for grab in grab_methods[1:]:
                    grab_method = '{}, {}'.format(grab_method, grab)
            self.channel_widget.setText("{} | {}".format(video.channel_title, grab_method))
        else:
            self.channel_widget.setText(self.video.channel_title)

        vid_age = datetime.datetime.utcnow() - self.video.date_published
        self.date_widget.setText(self.strf_delta(vid_age, "{hours}:{minutes}:{seconds}", "{days} days "))
        self.color_old_video(vid_age)
        self.color_live_video()

        self.set_thumbnail_pixmap(video.thumbnail_path)

    @staticmethod
    def strf_delta(tdelta, hours, days):
        d = {}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        if int(tdelta.days) > 0:
            return_string = "{}{}".format(days.format(days=tdelta.days), hours.format(**d))
        else:
            return_string = "{}".format(hours.format(**d))

        return return_string

    def color_old_video(self, vid_age, days=1):
        """
        Colors the QPalette background element of a video grey if it is older than days (default: 1)

        :param days:
        :param vid_age:
        :return:
        """
        if read_config('Gui', 'grey_old_videos'):
            if vid_age > datetime.timedelta(days):
                pal = self.palette()
                pal.setColor(QPalette.Window, Qt.lightGray)
                self.setAutoFillBackground(True)
                self.setPalette(pal)
            else:
                pal = self.palette()
                pal.setColor(QPalette.Window, Qt.white)
                self.setAutoFillBackground(True)
                self.setPalette(pal)

    def color_live_video(self, logging=False):
        """
        Colors the QPalette background element of a video in the following manner:
        Livestream:                 darkRed
        Upcoming/Scheduled stream:  darkYellow
        Premiere:                   darkMagenta

        :return:
        """
        if self.video.kind is VIDEO_KIND_LIVE:
            pal = self.palette()
            pal.setColor(QPalette.Window, Qt.darkRed)
            self.setAutoFillBackground(True)
            self.setPalette(pal)
        elif self.video.kind is VIDEO_KIND_LIVE_SCHEDULED:
            pal = self.palette()
            pal.setColor(QPalette.Window, Qt.darkYellow)
            self.setAutoFillBackground(True)
            self.setPalette(pal)
        elif self.video.kind is VIDEO_KIND_PREMIERE:
            pal = self.palette()
            pal.setColor(QPalette.Window, Qt.darkMagenta)
            self.setAutoFillBackground(True)
            self.setPalette(pal)
        else:
            # Set a default palette to reset any colouring.
            pal = self.palette()
            self.setAutoFillBackground(True)
            self.setPalette(pal)

    def set_tool_tip(self):
        if not read_config('Debug', 'disable_tooltips'):
            if read_config('Gui', 'tooltip_pictures'):
                text_element = read_config('Gui', 'tooltip_picture_size')
                thumb_width = read_config('Gui', 'tooltip_picture_width')
                thumb_height = read_config('Gui', 'tooltip_picture_height')
                resized_thumb = resize_thumbnail(self.video.thumbnail_path, thumb_width, thumb_height)

                self.setToolTip("<{} style='text-align:center;'><img src={} style='float:below'>{}: {}</{}>".format(
                    text_element, resized_thumb, self.video.channel_title, self.video.title, text_element))
            else:
                self.setToolTip("{}: {}".format(self.video.channel_title, self.video.title))

    def copy_url(self):
        """
        Copy selected video URL(s) to clipboard
        :return:
        """
        self.clipboard.setText(self.video.url_video)
        self.status_bar.showMessage('Copied URL to clipboard: {}'.format(self.video))

    def mark_downloaded(self):
        """
        Mark the video as downloaded
        :return:
        """
        logger.info('Mark downloaded: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Downloaded: {}'.format(self.video))
        self.video.date_downloaded = datetime.datetime.utcnow()
        if read_config('Gui', 'enable_auto_copy_to_clipboard'):
            self.copy_url()
        if read_config('Youtube-dl', 'use_youtube_dl'):
            self.status_bar.showMessage('Downloading video with youtube-dl: {}'.format(self.video))
        self.parent.main_model.playback_grid_view_listener.tileDownloaded.emit(self.video)
        # Update Subfeed to remove the video from its list unless show_downloaded=True.
        if not read_config('SubFeed', 'show_downloaded'):
            self.parent.main_model.subfeed_grid_view_listener.videosChanged.emit()

    def mark_discarded(self):
        """
        Mark the video as discarded
        :return:
        """
        logger.info('Mark discarded: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Discarded: {}'.format(self.video))
        self.status_bar.showMessage('Discarded: {}'.format(self.video))

        self.history.add(self.video, self.mark_discarded, self.unmark_discarded)

    def unmark_discarded(self):
        """
        Mark the video as un-discarded
        :return:
        """
        logger.info('Un-discarded: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Un-discarded: {} '.format(self.video))
        self.status_bar.showMessage('Un-discarded: {}'.format(self.video))

        self.history.add(self.video, self.unmark_discarded, self.mark_discarded)

    def mark_premiere(self):
        """
        Mark the video as live broadcast content (premiere)

        A premiere is: upcoming stream --> live stream --> vod
        :return:
        """
        logger.info('Marked as premiere: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Marked as premiere: {} '.format(self.video))
        self.status_bar.showMessage('Marked as premiere: {}'.format(self.video))
        self.color_live_video()

        self.history.add(self.video, self.mark_premiere, self.unmark_premiere)

    def unmark_premiere(self):
        """
        Unmark the video as live broadcast content (premiere)

        A premiere is: upcoming stream --> live stream --> vod
        :return:
        """
        logger.info('Unmarked as premiere: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Unmarked as premiere: {} '.format(self.video))
        self.status_bar.showMessage('Unmarked as premiere: {}'.format(self.video))
        self.color_live_video()

        self.history.add(self.video, self.unmark_premiere, self.mark_premiere)

    def mark_livestream_upcoming(self):
        """
        Mark the video as live broadcast content (upcoming)
        :return:
        """
        logger.info('Marked as livestream: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Marked as livestream: {} '.format(self.video))
        self.status_bar.showMessage('Marked as livestream: {}'.format(self.video))
        self.color_live_video()

        self.history.add(self.video, self.mark_livestream_upcoming, self.unmark_livestream_upcoming)

    def unmark_livestream_upcoming(self):
        """
        Unmark the video as live broadcast content (upcoming)
        :return:
        """
        logger.info('Unmarked as upcoming livestream: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Unmarked as upcoming livestream: {} '.format(self.video))
        self.status_bar.showMessage('Unmarked as upcoming livestream: {}'.format(self.video))
        self.color_live_video()

        self.history.add(self.video, self.unmark_livestream_upcoming, self.mark_livestream_upcoming)

    def mark_livestream(self):
        """
        Mark the video as live broadcast content (live)
        :return:
        """
        logger.info('Marked as livestream: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Marked as livestream: {} '.format(self.video))
        self.status_bar.showMessage('Marked as livestream: {}'.format(self.video))
        self.color_live_video()

        self.history.add(self.video, self.mark_livestream, self.unmark_livestream)

    def unmark_livestream(self):
        """
        Unmark the video as live broadcast content (live)
        :return:
        """
        logger.info('Unmarked as livestream: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Unmarked as livestream: {} '.format(self.video))
        self.status_bar.showMessage('Unmarked as livestream: {}'.format(self.video))
        self.color_live_video()

        self.history.add(self.video, self.unmark_livestream, self.mark_livestream)

    def mark_watched(self):
        """
        Mark the video as watched
        :return:
        """
        logger.debug('Mark watched: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Watched: {}'.format(self.video))
        self.history.add(self.video, self.mark_watched, self.unmark_watched)

    def unmark_watched(self):
        """
        Mark the video as Unwatched
        :return:
        """
        logger.debug('Mark Unwatched: {:2d}: {}'.format(self.id, self.video))
        update_plaintext_history('Unwatched: {}'.format(self.video))

        self.history.add(self.video, self.unmark_watched, self.mark_watched)

    # Get the system clipboard contents
    def clipboard_changed(self):
        text = self.clipboard().text()
        logger.info(text)

        self.b.insertPlainText(text + '\n')

    def decrease_prio(self):
        self.history.add(self.video, self.decrease_prio, self.increase_prio)

    def increase_prio(self):
        self.history.add(self.video, self.increase_prio, self.decrease_prio)
