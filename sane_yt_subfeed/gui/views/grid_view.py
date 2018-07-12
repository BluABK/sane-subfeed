import os
import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, qApp, QMenu, QGridLayout, QLabel, QVBoxLayout, QLineEdit, QApplication
from PyQt5.QtGui import QPixmap, QPainter

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.database.read_operations import refresh_and_get_newest_videos, \
    get_newest_stored_videos


class ExtendedQLabel(QLabel):

    def __init__(self, parent, video, img_id, clipboard, status_bar):
        QLabel.__init__(self, parent)
        # self.clipboard().dataChanged.connect(self.clipboard_changed)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.video = video
        self.set_video(video)
        self.img_id = img_id

    def setPixmap(self, p):
        self.p = p

    def set_video(self, video):
        self.video = video
        self.set_tool_tip()
        self.setPixmap(QPixmap(video.thumbnail_path))

    def set_tool_tip(self):
        if not read_config('Debug', 'disable_tooltips'):
            self.setToolTip("{}: {}".format(self.video.channel_title, self.video.title))

    def paintEvent(self, event):
        if self.p:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p)

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
        print('Mark downloaded: {:2d}: {} {} - {}'.format(self.img_id, self.video.url_video, self.video.channel_title,
                                                          self.video.title))
        self.video.downloaded = True
        UpdateVideo(self.video, update_existing=True).start()
        self.copy_url()

    def mark_discarded(self):
        """
        Mark the video as discarded
        :return:
        """
        print('Mark discarded: {:2d}: {} {} - {}'.format(self.img_id, self.video.url_video, self.video.channel_title,
                                                         self.video.title))
        self.video.discarded = True
        UpdateVideo(self.video, update_existing=True).start()
        self.status_bar.showMessage('Dismissed: {} ({} - {})'.format(self.video.url_video,
                                                                     self.video.channel_title,
                                                                     self.video.title))

    # Get the system clipboard contents
    def clipboard_changed(self):
        text = self.clipboard().text()
        print(text)

        self.b.insertPlainText(text + '\n')


class GridView(QWidget):
    q_labels = []
    items_x = None
    items_y = None

    def __init__(self, parent, clipboard, status_bar, vid_limit=100):
        super(GridView, self).__init__(parent)
        self.vid_limit = vid_limit
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.init_ui()

    def init_ui(self):
        # self.setGeometry(500, 500, 300, 220)

        grid = QGridLayout()
        grid.setSpacing(10)

        sublayout = QVBoxLayout()
        label1 = QLabel('AAAAAAAAAAAAAAAA')
        line_edit1 = QLineEdit()
        sublayout.addWidget(label1)
        # sublayout.addWidget(line_edit1)
        # grid.addLayout(sublayout, 4, 0, 1, 3)

        self.setLayout(grid)

        # video_item = "Video.thumb"
        # FIXME: Will break if user specifies a grid larger than this list
        video_item = sublayout
        items = [video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item]

        self.items_x = read_config('Gui', 'grid_view_x')
        self.items_y = read_config('Gui', 'grid_view_y')

        positions = [(i, j) for i in range(self.items_y) for j in range(self.items_x)]

        counter = 0
        filter_dl = read_config('Gui', 'hide_downloaded')
        start_with_stored_videos = read_config('Debug', 'start_with_stored_videos')

        if start_with_stored_videos:
            subscription_feed = get_newest_stored_videos(self.vid_limit, filter_downloaded=filter_dl)
            if len(subscription_feed) < 1:
                print('Used start_with_stored_videos=True, but there where no stored videos found')
                print('Get new videos? (y)')
                user_response = input()
                if user_response == 'n':
                    exit(1)
                else:
                    subscription_feed = refresh_and_get_newest_videos(self.vid_limit, filter_downloaded=filter_dl)
        else:
            subscription_feed = refresh_and_get_newest_videos(self.vid_limit, filter_downloaded=filter_dl)
        # print(positions)
        for position, video_layout in zip(positions, items):
            if counter >= len(items):
                break
            if items == '':  # FIXME: Replace with None for making a blank slot, and also implement better.
                continue
            # print(paths[counter])
            filename = subscription_feed[counter].thumbnail_path
            lbl = ExtendedQLabel(self, subscription_feed[counter], counter, self.clipboard, self.status_bar)
            self.q_labels.append(lbl)
            video_layout.addWidget(QLabel(filename))
            grid.addWidget(lbl, *position)

            counter += 1
