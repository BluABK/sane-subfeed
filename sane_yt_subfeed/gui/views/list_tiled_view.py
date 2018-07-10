import os

# from PyQt5.QtWidgets import QWidget, QMessageBox, qApp, \
#     QMenu, QGridLayout, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout
# from PyQt5.QtGui import QPixmap, QPainter
# from sqlalchemy import desc

# TODO: Easier to work with wildcard imports from PyQt, fix afterwards
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.insert_operations import UpdateVideo
from sane_yt_subfeed.database.select_operations import refresh_and_get_newest_videos, \
    get_newest_stored_videos

# Constants
OS_PATH = os.path.dirname(__file__)
ICO_PATH = os.path.join(OS_PATH, '..', 'icons')
DUMMY_ICO_PATH = os.path.join(OS_PATH, '..', 'icons', 'dummies')


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


class ListTiledView(QWidget):
    """
    |------------------------------------------------------------------------------------------------------------------|
    |  ChannelICO?                  | Channel title                                                                    |
    |------------------------------------------------------------------------------------------------------------------|
    |           T          l        | Video title                                                                      |
    |             h       i         |----------------------------------------------------------------------------------|
    |              u     a          | View count | Date published | Other                                              |
    |                m  n           |----------------------------------------------------------------------------------|
    |                  b            | Video description                                                                |
    |-------------------------------|----------------------------------------------------------------------------------|
    VBox( // Container
    VBox(HBox(ico, ch_title), HBox(thumb, VBox(video_title, HBox(views, date, other), desc)) // Video
        ...)

    VBox(
        HBox(ico, ch_title), HBox(thumb, VBox(video_title, HBox(views, date, other), desc)
        )

    VBox(
        HBox(
            ico, ch_title
            ), HBox(
                                thumb, VBox(
                                            video_title, HBox(
                                                                views, date, other
                                                             ), desc
                                            )
                    )
    """
    eqlabels = None

    def __init__(self, clipboard, status_bar, vid_limit=40):
        super().__init__()
        self.eqlabels = []
        self.vid_limit = vid_limit
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.init_ui()

    def init_ui(self):
        # The layouts
        layout_container = QVBoxLayout()
        # layout_container = QGridLayout()
        layout_video_item = QVBoxLayout()
        layout_video_item_header = QHBoxLayout()
        layout_video_item_body = QHBoxLayout()
        layout_video_item_body_info = QVBoxLayout()
        layout_video_item_body_info_stats = QHBoxLayout()
        self.setLayout(layout_container)


        # #### DUMMY SECTION ######
        dummies = ['Alica Skipper', 'Collette Halstead', 'Melonie Wirth', 'Theo Alonso', 'Alex Golden', 'Brande Taber',
                   'Hank Doty', 'Dominque Baumgartner', 'Charlsie Stoner', 'Lovella Mckee']
        # Dummy Video Item 1
        # dummy1_chico = QLabel(QIcon(os.path.join(DUMMY_ICO_PATH, 'd1.png')))
        dummy1_chico = QLabel('ICO.bork')
        dummy1_chtitle = QLabel(dummies[0])
        # dummy1_thumb = ExtendedQLabel(self, subscription_feed[counter], counter, self.clipboard, self.status_bar)
        # self.eq_labels.append(dummy1_thumb)

        filter_dl = read_config('Gui', 'hide_downloaded')
        videos = get_newest_stored_videos(self.vid_limit, filter_downloaded=filter_dl)

        # DUMMY TESTING
        for i in range(5):
            layout_video_item_header.addWidget(QLabel('ICO.bork'))
            layout_video_item_header.addWidget(QLabel('video.channel_title'))

            # thumb_filename = video.thumbnail_path
            # thumb_label = ExtendedQLabel(self, video, counter, self.clipboard, self.status_bar)
            # self.eqlabels.append(thumb_label)
            layout_video_item_body.addWidget(QLabel('thumb_filename'))
            layout_video_item_body.addWidget(QLabel('Dummy Thumb'))
            layout_video_item_body_info.addWidget(QLabel('video.title'))
            layout_video_item_body_info_stats.addWidget(QLabel('NaN views'))
            layout_video_item_body_info_stats.addWidget(QLabel('video.date_published'))
            layout_video_item_body_info_stats.addWidget(QLabel('No Other info specified'))
            layout_video_item_body_info.addWidget(QLabel('video.description'))

        # counter = 0
        # for video in videos:
        #     layout_video_item_header.addWidget(dummy1_chico)
        #     layout_video_item_header.addWidget(QLabel(video.channel_title))
        #
        #     thumb_filename = video.thumbnail_path
        #     thumb_label = ExtendedQLabel(self, video, counter, self.clipboard, self.status_bar)
        #     self.eqlabels.append(thumb_label)
        #     # layout_video_item_body.addWidget(QLabel(thumb_filename))
        #     layout_video_item_body.addWidget(QLabel('Dummy Thumb'))
        #     layout_video_item_body_info.addWidget(QLabel(video.title))
        #     layout_video_item_body_info_stats.addWidget(QLabel('NaN views'))
        #     layout_video_item_body_info_stats.addWidget(QLabel(video.date_published.isoformat(' ').split('.')[0]))
        #     layout_video_item_body_info_stats.addWidget(QLabel('No Other info specified'))
        #     layout_video_item_body_info.addWidget(QLabel(video.description))

            # layout_video_item_body_info.addLayout(layout_video_item_body_info_stats)
            # layout_video_item.addLayout(layout_video_item_header)
            # layout_video_item_body.addLayout(layout_video_item_body_info)
            # layout_video_item.addLayout(layout_video_item_body)
            # layout_container.addLayout(layout_video_item)

            # counter += 1
        layout_container.addLayout(layout_video_item)
        layout_video_item.addLayout(layout_video_item_header)
        layout_video_item_body_info.addLayout(layout_video_item_body_info_stats)
        layout_video_item_body.addLayout(layout_video_item_body_info)
        layout_video_item.addLayout(layout_video_item_body)

        self.show()
