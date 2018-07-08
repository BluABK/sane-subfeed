# PyCharm bug: PyCharm seems to be expecting the referenced module to be included in an __all__ = [] statement
from PyQt5.Qt import QClipboard
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QBasicTimer
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QAction, qApp, \
    QMenu, QGridLayout, QProgressBar, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter

from ..thumbnail_handler import download_thumbnails_threaded, get_thumbnail_path


class ExtendedQLabel(QLabel):

    def __init__(self, parent, img_id, video, clipboard, status_bar):
        QLabel.__init__(self, parent)
        self.img_id = img_id
        self.video = video
        # self.clipboard().dataChanged.connect(self.clipboard_changed)
        self.clipboard = clipboard
        self.status_bar = status_bar

    def setPixmap(self, p):
        self.p = p

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
                                                                             self.video.channel_title, self.video.title))

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
    subfeed = None

    def __init__(self, subfeed, clipboard, status_bar):
        super().__init__()
        self.subfeed = subfeed
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
        # for position, name in zip(positions, items):
        download_thumbnails_threaded(self.subfeed)
        print(positions)
        for position, video_layout in zip(positions, items):
            if counter >= len(items):
                break
            if items == '':
                continue
            # if name == 'SAMPLE TITLE':
            #     filename = "{}.jpg".format(counter)
            #     lbl = QLabel(filename)
            #     print("adding TITLE to pos: {}".format(filename, *position))
            #     grid.addWidget(lbl, *position)
            # else:
            # button = QPushButton(name)
            # filename = "{}.jpg".format(counter)
            try:

                filename = get_thumbnail_path(self.subfeed[counter])
            except:
                print(counter)
                # print(len(file_list))
                raise
            pixmap = QPixmap(filename)
            lbl = ExtendedQLabel(self, counter, self.subfeed[counter], self.clipboard)
            lbl.setPixmap(pixmap)
            # lbl.setToolTip("Video {}".format(counter))
            lbl.setToolTip("{}: {}".format(self.subfeed[counter].channel_title, self.subfeed[counter].title))
            video_layout.addWidget(QLabel(filename))
            # grid.addLayout(video_layout, *position)
            print("adding {} to pos: {}".format(filename, *position))
            grid.addWidget(lbl, *position)
            # print(grid.children()[0].alignment)

            counter += 1
        print(grid)
                # grid.addChildWidget(QLabel(filename))

        # QToolTip.setFont(QFont('SansSerif', 10))
        #
        # # self.setToolTip('This is a <b>QWidget</b> widget')
        # btn = QPushButton('Button 1', self)
        # btn.setToolTip('This is a <b>QPushButton</b> widget')
        # btn.clicked.connect(self.button_clicked)
        # btn.resize(btn.sizeHint())
        # btn.move(10, 50)
        #
        # qbtn = QPushButton('Quit', self)
        # qbtn.clicked.connect(QApplication.instance().quit)
        # qbtn.resize(qbtn.sizeHint())
        # qbtn.move(100, 50)
        #
        # self.setWindowTitle('Sane Subscription Feed, yo! [Grid]')
        # self.setWindowIcon(QIcon('blu.ico'))
        # self.statusBar().showMessage('Ready.')
        #

        # self.pbar = QProgressBar(self)
        # self.pbar.setGeometry(30, 40, 200, 25)
        #
        # self.btn = QPushButton('Start', self)
        # self.btn.move(40, 80)
        # # self.btn.clicked.connect(self.doAction)
        #
        # self.timer = QBasicTimer()
        # self.step = 0
        #
        # self.setGeometry(300, 300, 280, 170)
        # self.setWindowTitle('QProgressBar')
        # self.resize(1280, 800)  # Start at a sane 16:10 minsize since thumbs are scaling now
        # self.show()     # FIXME: conflict with MainWindow?

    def button_clicked(self):

        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')

    def btn1_event(self, event):
        reply = QMessageBox.question(self, 'Button', "BUTTON BUTTON BUTTON BUTTON!", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def quit_query(self, event):
        reply = QMessageBox.question(self, 'Quit?', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)


# TODO: Remove after debugging is done
# import sys
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = GridView(None)
#
#     sys.exit(app.exec_())
