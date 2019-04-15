import sys

import os

import datetime
import subprocess
import webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from dateutil.relativedelta import relativedelta
from string import Template

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.database.detached_models.video_d import VIDEO_KIND_VOD, VIDEO_KIND_LIVE, \
    VIDEO_KIND_LIVE_SCHEDULED, VIDEO_KIND_PREMIERE
from sane_yt_subfeed.gui.views.grid_view.labels.channel_label import ChannelLabel
from sane_yt_subfeed.gui.views.grid_view.labels.date_label import DateLabel
from sane_yt_subfeed.gui.views.grid_view.labels.title_label import TitleLabel
from sane_yt_subfeed.handlers.plaintext_history_handler import update_plaintext_history
from sane_yt_subfeed.handlers.log_handler import logger, create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import resize_thumbnail


class DeltaTemplate(Template):
    delimiter = "$"


class VideoTile(QWidget):
    hotkey_ctrl_down = False

    def __init__(self, parent, video, vid_id, clipboard, status_bar):
        QWidget.__init__(self, parent=parent)
        self.logger = create_logger(__name__)
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

        self.layout = QGridLayout()
        self.layout.setSpacing(0)  # Don't use Qt's "global padding" spacing.
        self.layout.setAlignment(Qt.AlignTop)
        # Make sure layout items don't overlap
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.thumbnail_label = self.init_thumbnail_tile()
        self.title_label = TitleLabel(video.title, self)
        self.channel_label = ChannelLabel(video.channel_title, self)
        self.date_label = DateLabel('', self)

        # Use a blank QLabel as spacer item for increased control of spacing (avoids global padding).
        spacer_label = QLabel()
        spacer_label.setFixedHeight(read_config('GridView', 'tile_line_spacing'))

        # Add labels to layout
        self.layout.addWidget(self.thumbnail_label)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(spacer_label)
        self.layout.addWidget(self.channel_label)
        self.layout.addWidget(spacer_label)
        self.layout.addWidget(self.date_label)

        self.setLayout(self.layout)

        # Add video on the layout/tile.
        self.set_video(video)

        if read_config('Debug', 'color_tile_elements'):
            self.color_palette(Qt.green)
            self.thumbnail_label.setStyleSheet("QLabel { background-color : darkMagenta}")
            self.title_label.setStyleSheet("QLabel { background-color : crimson}")
            self.channel_label.setStyleSheet("QLabel { background-color : darkGreen}")
            self.date_label.setStyleSheet("QLabel { background-color : gray}")

    def init_thumbnail_tile(self):
        raise ValueError("ThumbnailTile initialised from VideoTile, not subclass!")

    def set_thumbnail_pixmap(self, thumbnail_path):
        """
        Runs
        :return:
        """
        self.thumbnail_label.setPixmap(QPixmap(thumbnail_path))
        self.update()

    def set_video(self, video):
        self.video = video
        self.set_tool_tip()

        self.channel_label.setText(self.video.channel_title)

        self.date_label.setText(self.strf_delta(self.video.date_published))
        self.color_old_video(self.video.date_published)
        self.color_live_video()

        self.set_thumbnail_pixmap(video.thumbnail_path)

    def get_default_player(self):
        """
        Returns the default media player.
        :return:
        """
        config_default_player = self.str_to_list(read_config('Player', 'default_player', literal_eval=False))
        if config_default_player:
            return config_default_player
        else:
            return None

    def open_in_player(self, path, player=None, mark_watched=True, isfile=True):
        """
        Opens a video (defined by path) in a given media player
        :param isfile:          If False path is an url, skip os existence checks.
        :param path:            Can be file path or URL.
        :param player:          Absolute path to a media player application.
        :param mark_watched:    Whether or not to mark video as watched.
        :return:
        """
        if not player:
            player = self.get_default_player()
        if mark_watched:
            self.mark_watched()
        self.logger.info('Playing {}, with player: {}'.format(path, player))
        if isfile and not os.path.isfile(path):
            self.logger.warning('os.path.isfile returns False for File: {}'.format(path))
        if player:
            popen_args = player + [path]
            if sys.platform.startswith('linux'):
                popen_args.insert(0, 'nohup')
                subprocess.Popen(popen_args, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(popen_args)

    def open_in_browser(self, mark_watched=True):
        """
        Opens the video URL in a web browser, if none is specified it will guess the default
        using the webbrowser module.
        :param mark_watched: Whether or not to mark video as watched.
        :return:
        """
        if mark_watched:
            self.mark_watched()
        self.logger.info('Playing {}, in web browser'.format(self.video))
        specific_browser = read_config('Player', 'url_player', literal_eval=False)
        if specific_browser:
            popen_args = [specific_browser, self.video.url_video]
            if sys.platform.startswith('linux'):
                popen_args.insert(0, 'nohup')
                subprocess.Popen(popen_args, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(popen_args)
        else:
            webbrowser.open_new_tab(self.video.url_video)

    @staticmethod
    def str_to_list(s):
        """
        Transform a space delimited string to a list of substrings.
        Returns s as-is if False.
        :param s:
        :return:
        """
        if s:
            return s.split(' ')
        else:
            return s

    @staticmethod
    def str_to_list_destructive(s):
        """
        Destructively transform a space delimited string to a list of substrings.
        Does nothing If string is False.
        :param s:
        :return:
        """
        if s:
            s = s.split(' ')

    @staticmethod
    def determine_name(name, failover_name):
        if name:
            return name
        else:
            return failover_name

    @staticmethod
    def strf_delta(date_published, fmt=None):
        tdelta = relativedelta(date_published, datetime.datetime.utcnow())
        d = {
            'decadesdecades': "{0:02d}".format(int(abs(tdelta.years / 10))),
            'decades': int(abs(tdelta.years) / 10),
            'ydyd': "{0:02d}".format(abs(tdelta.years)),
            'yd': abs(tdelta.years),
            'mm': "{0:02d}".format(abs(tdelta.months)),
            'm': abs(tdelta.months),
            'dd': "{0:02d}".format(abs(tdelta.days)),
            'd': abs(tdelta.days),
            'HH': "{0:02d}".format(abs(tdelta.hours)),
            'H': abs(tdelta.hours),
            'MM': "{0:02d}".format(abs(tdelta.minutes)),
            'M': abs(tdelta.minutes),
            'SS': "{0:02d}".format(abs(tdelta.seconds)),
            'S': abs(tdelta.seconds),
            'f': abs(tdelta.microseconds)
        }

        if fmt is None:
            if int(abs(tdelta.years)) > 10:
                fmt = read_config('GridView', 'timedelta_format_decades', literal_eval=False)
                # Update years in relation to decade
                d['yd'] = d['yd'] - 10
                d['ydyd'] = "{0:02d}".format(abs(d['yd']))
            elif int(abs(tdelta.years)) > 0:
                fmt = read_config('GridView', 'timedelta_format_years', literal_eval=False)
            elif int(abs(tdelta.months)) > 0:
                fmt = read_config('GridView', 'timedelta_format_months', literal_eval=False)
            elif int(abs(tdelta.days)) > 0:
                fmt = read_config('GridView', 'timedelta_format_days', literal_eval=False)
            else:
                fmt = read_config('GridView', 'timedelta_format', literal_eval=False)

        t = DeltaTemplate(fmt)

        return t.substitute(**d)

    def color_palette(self, color, role=QPalette.Window, log_facility=None, log_msg=""):
        """
        Colors a given palette.
        :param palette:
        :param color: A Qt color integer
        :param role: Which QPalette role to apply color to (default: background)
        :param log_facility: if set, log to this facility
        :param log_msg:
        :return:
        """
        if log_facility:
            log_facility("Coloring tile ({}): {}" .format(log_msg, self.video))
        palette = self.palette()
        # Set color if specified, if not skip this to create a default/reset palette.
        if color:
            palette.setColor(role, color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def color_old_video(self, date_published, days=1):
        """
        Colors the QPalette background element of a video grey if it is older than days (default: 1)

        :param days:
        :param date_published:
        :return:
        """
        if read_config('Gui', 'grey_old_videos'):
            vid_age = datetime.datetime.utcnow() - date_published
            if vid_age > datetime.timedelta(days):
                self.color_palette(Qt.lightGray)
            else:
                self.color_palette(Qt.white)

    def color_live_video(self):
        """
        Colors the QPalette background element of a video in the following manner:
        Livestream:                 darkRed
        Upcoming/Scheduled stream:  darkYellow
        Premiere:                   darkMagenta

        :return:
        """
        if self.video.kind == VIDEO_KIND_LIVE:
            self.color_palette(Qt.darkRed, log_facility=self.logger.info, log_msg="liveBroadcastContent: live")
        elif self.video.kind == VIDEO_KIND_LIVE_SCHEDULED:
            self.color_palette(Qt.darkYellow, log_facility=self.logger.info, log_msg="liveBroadcastContent: upcoming")
        elif self.video.kind == VIDEO_KIND_PREMIERE:
            self.color_palette(Qt.darkMagenta, log_facility=self.logger.info, log_msg="liveBroadcastContent: premiere")
        elif self.video.kind == VIDEO_KIND_VOD:
            # Set a default palette to reset any colouring.
            self.color_palette(None, log_msg="vod")
        elif self.video.kind is None:
            # Set a default palette to reset any colouring. Account for cases that predate implementation of kind.
            self.color_palette(None)
        else:
            # Set a default palette to reset any colouring. Account for edge cases with invalid kind.
            self.color_palette(None, log_facility=self.logger.error, log_msg="invalid kind: {}".format(self.video.kind))

    def set_tool_tip(self):
        if not read_config('Debug', 'disable_tooltips'):
            if read_config('Gui', 'tooltip_pictures'):
                text_element = read_config('Gui', 'tooltip_picture_size')
                thumb_width = read_config('Gui', 'tooltip_picture_width')
                thumb_height = read_config('Gui', 'tooltip_picture_height')
                resized_thumb = resize_thumbnail(self.video.thumbnail_path, thumb_width, thumb_height)

                self.setToolTip("<{} style='text-align:center;'><img src={} style='float:below'><br/>{}: {}</{}>".format(
                    text_element, resized_thumb, self.video.channel_title, self.video.title, text_element))
            else:
                self.setToolTip("{}: {}".format(self.video.channel_title, self.video.title))

    def copy_url(self, mark_watched=False):
        """
        Copy selected video URL(s) to clipboard
        :return:
        """
        if mark_watched:
            self.mark_watched()
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
