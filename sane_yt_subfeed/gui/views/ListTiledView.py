from PyQt5.QtWidgets import QWidget, QMessageBox, qApp, \
    QMenu, QGridLayout, QLabel, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QPixmap, QPainter
from sqlalchemy import desc

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.insert_operations import UpdateVideo
from sane_yt_subfeed.database.select_operations import refresh_and_get_newest_videos, \
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

    VBox(HBox(ico, ch_title), HBox(thumb, VBox(video_title, HBox(views, date, other), desc))

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
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        # grid.setSpacing(10)


        self.show()
