import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QMenu, qApp, QSizePolicy

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.grid_view.thumbnail_tile import ThumbnailTile
from sane_yt_subfeed.gui.views.grid_view.title_tile import TitleTile
from sane_yt_subfeed.gui.views.grid_view.channel_tile import ChannelTile
from sane_yt_subfeed.gui.views.grid_view.date_tile import DateTile
from sane_yt_subfeed.log_handler import logger
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.youtube.youtube_requests import list_uploaded_videos_search, get_channel_uploads, \
    list_uploaded_videos


class VideoTile(QWidget):

    def __init__(self, parent, video, id, clipboard, status_bar):
        QWidget.__init__(self, parent=parent)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.video = video
        self.id = id
        self.parent = parent

        self.pref_height = read_config('Gui', 'tile_pref_height')
        self.pref_width = read_config('Gui', 'tile_pref_width')
        self.setFixedSize(self.pref_width, self.pref_height)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 4)
        self.thumbnail_widget = ThumbnailTile(self)
        self.layout.addWidget(self.thumbnail_widget)

        self.title_widget = TitleTile(video.title, self)
        self.layout.addWidget(self.title_widget)
        self.channel_widget = ChannelTile(video.channel_title, self)
        self.layout.addWidget(self.channel_widget)

        self.date_widget = DateTile('', self)
        self.layout.addWidget(self.date_widget)

        self.setLayout(self.layout)

        self.set_video(video)

    def resizeEvent(self, event):
        pass
        # self.title_widget.update_font()
        #
        # self.channel_widget.update_font()
        #
        # self.date_widget.update_font()

    def set_video(self, video):
        self.video = video
        self.set_tool_tip()
        self.title_widget.update_font()

        show_grab_method = read_config('Debug', 'show_grab_method')
        if show_grab_method:
            grab_method = self.debug_grab_method(video)
            self.channel_widget.setText("{} | {}".format(video.channel_title, grab_method))
        else:
            self.channel_widget.setText(self.video.channel_title)

        vid_age = datetime.datetime.now() - self.video.date_published
        self.date_widget.setText(format(vid_age))
        if read_config('Gui', 'grey_old_videos'):
            if vid_age > datetime.timedelta(days=1):
                pal = self.palette()
                pal.setColor(QPalette.Background, Qt.lightGray)
                self.setAutoFillBackground(True)
                self.setPalette(pal)
            else:
                pal = self.palette()
                pal.setColor(QPalette.Background, Qt.white)
                self.setAutoFillBackground(True)
                self.setPalette(pal)

        self.thumbnail_widget.setPixmap(QPixmap(video.thumbnail_path))

        self.update()

    def set_tool_tip(self):
        if not read_config('Debug', 'disable_tooltips'):
            self.setToolTip("{}: {}".format(self.video.channel_title, self.video.title))

    def mousePressEvent(self, QMouseEvent):
        """
        Override mousePressEvent to support mouse button actions
        :param QMouseEvent:
        :return:
        """
        if QMouseEvent.button() == Qt.MidButton:
            self.mark_discarded()
        elif QMouseEvent.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            print("Not Implemented: Select video")
        elif QMouseEvent.button() == Qt.LeftButton:
            self.mark_downloaded()

    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
        menu = QMenu(self)
        copy_url_action = menu.addAction("Copy link")
        downloaded_item_action = menu.addAction("Copy link and mark as downloaded")
        discard_item_action = menu.addAction("Discard video")
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_url_action:
            self.copy_url()
        elif action == downloaded_item_action:
            self.mark_downloaded()
        elif action == discard_item_action:
            self.mark_discarded()
        elif action == quit_action:
            qApp.quit()

    def copy_url(self):
        """
        Copy selected video URL(s) to clipboard
        :return:
        """
        self.clipboard.setText(self.video.url_video)
        self.status_bar.showMessage('Copied URL to clipboard: {} ({} - {})'.format(self.video.url_video,
                                                                                   self.video.channel_title,
                                                                                   self.video.title))

    def mark_downloaded(self):
        """
        Mark the video as downloaded
        :return:
        """
        logger.info('Mark downloaded: {:2d}: {} {} - {}'.format(self.id, self.video.url_video, self.video.channel_title,
                                                                self.video.title))
        self.video.downloaded = True
        self.parent.main_model.grid_view_listener.tileDownloaded.emit(self.video, self.id)
        self.copy_url()

    def mark_discarded(self):
        """
        Mark the video as discarded
        :return:
        """
        logger.info('Mark discarded: {:2d}: {} {} - {}'.format(self.id, self.video.url_video, self.video.channel_title,
                                                               self.video.title))
        self.video.discarded = True
        self.parent.main_model.grid_view_listener.tileDiscarded.emit(self.video, self.id)
        self.status_bar.showMessage('Dismissed: {} ({} - {})'.format(self.video.url_video,
                                                                     self.video.channel_title,
                                                                     self.video.title))

    # Get the system clipboard contents
    def clipboard_changed(self):
        text = self.clipboard().text()
        logger.info(text)

        self.b.insertPlainText(text + '\n')

    def debug_grab_method(self, video):
        """
        Shows if a channel was crawled using list() or search()
        :param video:
        :return:
        """
        grab_method = "N/A"
        use_tests = read_config('Requests', 'use_tests')
        if use_tests:
            channel = db_session.query(Channel).get(video.channel_id)
            miss = read_config('Requests', 'miss_limit')
            pages = read_config('Requests', 'test_pages')
            extra_pages = read_config('Requests', 'extra_list_pages')
            used_list = False
            list_pages = 0
            for test in channel.tests:
                if test.test_pages > list_pages:
                    list_pages = test.test_pages
                if test.test_miss < miss or test.test_pages > pages:
                    used_list = True
                    db_session.remove()
                    grab_method = "search()"
                    break
            if not used_list:
                grab_method = "list()"
                db_session.remove()

        return grab_method
