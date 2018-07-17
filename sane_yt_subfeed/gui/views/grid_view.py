import datetime
import os
import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, qApp, QMenu, QGridLayout, QLabel, QVBoxLayout, QLineEdit, QApplication, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter, QFontMetrics, QPalette

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.database.read_operations import refresh_and_get_newest_videos, \
    get_newest_stored_videos
from sane_yt_subfeed.log_handler import logger


class ThumbnailTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setPixmap(self, p):
        self.p = p

    def paintEvent(self, event):
        if self.p:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p)


class TitleTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # def paintEvent( self, event ):
    #     painter = QPainter(self)
    #
    #     metrics = QFontMetrics(self.font())
    #     elided  = metrics.elidedText(self.text(), Qt.ElideRight, self.width()*1.9)
    #
    #     painter.drawText(self.rect(), self.alignment(), elided, Qt.TextWordWrap)


class ChannelTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class DateTile(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class VideoTile(QWidget):

    def __init__(self, parent, video, id, clipboard, status_bar):
        QWidget.__init__(self, parent)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.video = video
        self.id = id
        self.parent = parent

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout = QVBoxLayout()
        self.thumbnail_widget = ThumbnailTile(self)
        self.layout.addWidget(self.thumbnail_widget, 1)

        self.title_widget = TitleTile(video.title)
        self.title_widget.setWordWrap(True)
        self.layout.addWidget(self.title_widget)

        self.channel_widget = ChannelTile(video.channel_title)
        self.channel_widget.setWordWrap(True)
        self.layout.addWidget(self.channel_widget)

        self.date_widget = DateTile('')
        self.date_widget.setWordWrap(True)
        self.layout.addWidget(self.date_widget)

        self.setLayout(self.layout)

        self.set_video(video)

    def resizeEvent(self, event):
        # self.thumbnail_widget.set

        c_font = self.channel_widget.font()
        c_font.setPixelSize(self.height() * 0.07)
        self.channel_widget.setFont(c_font)

        t_font = self.title_widget.font()
        t_font.setPixelSize(self.height() * 0.07)
        self.title_widget.setFont(t_font)
        metrics = QFontMetrics(t_font)
        elided = metrics.elidedText(self.video.title, Qt.ElideRight, self.title_widget.width()*1.7)
        self.title_widget.setText(elided)

        d_font = self.date_widget.font()
        d_font.setPixelSize(self.height() * 0.07)
        self.date_widget.setFont(d_font)

        # self.title_widget.setFixedHeight(self.height()/5)
        # self.channel_widget.setFixedHeight(self.height()*(2/20))
        # self.date_widget.setFixedHeight(self.height()*(2/20))
        # self.thumbnail_widget.update()

    def set_video(self, video):
        self.video = video
        self.set_tool_tip()
        # self.setPixmap(QPixmap(video.thumbnail_path))
        self.title_widget.setText(self.video.title)
        self.channel_widget.setText(self.video.channel_title)

        vid_age = datetime.datetime.now() - self.video.date_published
        self.date_widget.setText(format(vid_age))
        if vid_age > datetime.timedelta(days=1):
            if read_config('Gui', 'grey_old_videos'):
                pal = self.palette()
                pal.setColor(QPalette.Background, Qt.lightGray)
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


class GridView(QWidget):
    q_labels = []
    items_x = None
    items_y = None
    main_model = None

    def __init__(self, parent, main_model: MainModel, clipboard, status_bar):
        super(GridView, self).__init__(parent)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.main_model = main_model

        self.init_ui()

    def init_ui(self):
        logger.info("Initializing GridView UI")

        self.main_model.grid_view_listener.hiddenVideosChanged.connect(self.videos_changed)

        grid = QGridLayout()
        # FIXME: QLabels don't fill
        grid.setSpacing(0)
        self.setLayout(grid)

        self.items_x = read_config('Gui', 'grid_view_x')
        self.items_y = read_config('Gui', 'grid_view_y')

        subscription_feed = self.main_model.filtered_videos

        counter = 0
        positions = [(i, j) for i in range(self.items_y) for j in range(self.items_x)]
        for position in positions:
            if counter >= len(positions):
                break
            lbl = VideoTile(self, subscription_feed[counter], counter, self.clipboard, self.status_bar)
            self.q_labels.append(lbl)
            grid.addWidget(lbl, *position)
            counter += 1

    def videos_changed(self):
        logger.info('GridView: Updating tiles')
        for q_label, video in zip(self.q_labels, self.main_model.filtered_videos):
            q_label.set_video(video)
