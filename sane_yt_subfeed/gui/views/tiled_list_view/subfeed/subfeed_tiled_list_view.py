from PyQt5.QtGui import *
# TODO: Easier to work with wildcard imports from PyQt, fix afterwards
from PyQt5.QtWidgets import *

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.handlers.log_handler import create_logger


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

    def paintEvent(self, paint_event: QPaintEvent):
        if self.p:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p)

        # Support stylesheets
        style_option = QStyleOption()
        style_option.initFrom(self)
        painter = QPainter(self)
        style = self.style()
        style.drawPrimitive(QStyle.PE_Widget, style_option, painter, self)

    def mouseReleaseEvent(self, ev):
        print('clicked {:2d}: {}'.format(self.img_id, self.video))
        self.clipboard.setText(self.video.url_video)
        self.video.downloaded = True
        UpdateVideo(self.video, update_existing=True).start()
        self.status_bar.showMessage('Copied URL to clipboard: {}'.format(self.video))

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


class SubfeedTiledListView(QWidget):
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

    def __init__(self, parent, vid_limit=40):
        super(SubfeedTiledListView, self).__init__(parent)
        self.logger = create_logger(__name__)
        self.root = parent  # MainWindow
        self.eqlabels = []
        self.vid_limit = vid_limit
        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar

        # The layouts
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        header_layout = QHBoxLayout()
        body_layout = QHBoxLayout()

        main_layout.addLayout(header_layout)
        main_layout.addLayout(body_layout)

        description_layout = QVBoxLayout()
        image_layout = QVBoxLayout()

        body_layout.addLayout(image_layout)
        body_layout.addLayout(description_layout)

        video_title_layout = QHBoxLayout()
        more_layout = QHBoxLayout()
        published_layout = QHBoxLayout()

        description_layout.addLayout(video_title_layout)
        description_layout.addLayout(more_layout)
        description_layout.addLayout(published_layout)

        video_title = QLabel('video title')
        view_count = QLabel('View count')
        date = QLabel('date')
        published = QLabel('more')
        view_description = QLabel('view description')
        image_label = QLabel('image')
        icon_label = QLabel('icon')
        title_label = QLabel('title')

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        image_layout.addWidget(image_label)

        video_title_layout.addWidget(video_title)
        more_layout.addWidget(view_count)
        more_layout.addWidget(date)
        more_layout.addWidget(published)
        description_layout.addWidget(view_description)

    def paintEvent(self, paint_event: QPaintEvent):
        """
        Override painEvent in order to support stylesheets.
        :param paint_event:
        :return:
        """
        style_option = QStyleOption()
        style_option.initFrom(self)
        painter = QPainter(self)
        style = self.style()
        style.drawPrimitive(QStyle.PE_Widget, style_option, painter, self)
