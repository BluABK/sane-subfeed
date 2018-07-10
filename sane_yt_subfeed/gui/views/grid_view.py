# PyCharm bug: PyCharm seems to be expecting the referenced module to be included in an __all__ = [] statement
import os
import time

from PyQt5.QtWidgets import QWidget, QMessageBox, qApp, \
    QMenu, QGridLayout, QLabel, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QPixmap, QPainter
from sqlalchemy import desc

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.database.read_operations import refresh_and_get_newest_videos, \
    get_newest_stored_videos
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.youtube.thumbnail_handler import thumbnails_dl_and_paths
from sane_yt_subfeed.youtube.update_videos import refresh_uploads


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
        self.setToolTip("{}: {}".format(self.video.channel_title, self.video.title))

    def paintEvent(self, event):
        if self.p:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p)

    def mouseReleaseEvent(self, ev):
        print('clicked {:2d}: {} {} - {}'.format(self.img_id, self.video.url_video, self.video.channel_title,
                                                 self.video.title))
        self.clipboard.setText(self.video.url_video)
        self.video.downloaded = True
        UpdateVideo(self.video, update_existing=True).start()
        self.status_bar.showMessage('Copied URL to clipboard: {} ({} - {})'.format(self.video.url_video,
                                                                                   self.video.channel_title,
                                                                                   self.video.title))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            qApp.quit()

    # Get the system clipboard contents
    def clipboard_changed(self):
        text = self.clipboard().text()
        print(text)

        self.b.insertPlainText(text + '\n')


class GridView(QWidget):
    q_labels = []

    def __init__(self, clipboard, status_bar, vid_limit=40):
        super().__init__()
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
        video_item = sublayout
        items = [video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item]

        positions = [(i, j) for i in range(5) for j in range(4)]

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
            if items == '':
                continue
            # print(paths[counter])
            filename = subscription_feed[counter].thumbnail_path
            lbl = ExtendedQLabel(self, subscription_feed[counter], counter, self.clipboard, self.status_bar)
            self.q_labels.append(lbl)
            video_layout.addWidget(QLabel(filename))
            grid.addWidget(lbl, *position)

            counter += 1
