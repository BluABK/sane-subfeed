# PyCharm bug: PyCharm seems to be expecting the referenced module to be included in an __all__ = [] statement
import os
import time

from PyQt5.Qt import QClipboard
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QBasicTimer
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QAction, qApp, \
    QMenu, QGridLayout, QProgressBar, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.pickle_handler import PICKLE_PATH, dump_pickle, load_pickle
from sane_yt_subfeed.thumbnail_handler import download_thumbnails_threaded, get_thumbnail_path, thumbnails_dl_and_paths


class ExtendedQLabel(QLabel):

    def __init__(self, parent, video, img_id, clipboard, status_bar):
        QLabel.__init__(self, parent)
        # self.clipboard().dataChanged.connect(self.clipboard_changed)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.video = video
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
    uploads = None
    q_labels = []

    def __init__(self, uploads, clipboard, status_bar):
        super().__init__()
        self.uploads = uploads
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
        use_dummy_data = read_config('Debug', 'use_dummy_uploads')
        if use_dummy_data:
            self.uploads = load_pickle(os.path.join(PICKLE_PATH, 'uploads_dump.pkl'))
        else:
            self.uploads.get_uploads()
            dump_pickle(self.uploads, os.path.join(PICKLE_PATH, 'uploads_dump.pkl'))
        paths = thumbnails_dl_and_paths(self.uploads.uploads[:30])
        # print(positions)
        for position, video_layout in zip(positions, items):
            if counter >= len(items):
                break
            if items == '':
                continue
            filename = paths[counter]
            lbl = ExtendedQLabel(self, self.uploads.uploads[counter], counter, self.clipboard, self.status_bar)
            lbl.set_video(self.uploads.uploads[counter])
            self.q_labels.append(lbl)
            video_layout.addWidget(QLabel(filename))
            grid.addWidget(lbl, *position)

            counter += 1
