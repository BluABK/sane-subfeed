# !/usr/bin/python3
# -*- coding: utf-8 -*-

# PyCharm bug: PyCharm seems to be expecting the referenced module to be included in an __all__ = [] statement
# noinspection PyUnresolvedReferences
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QBasicTimer
# noinspection PyUnresolvedReferences
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QAction, qApp, \
    QMenu, QGridLayout, QProgressBar, QLabel
# noinspection PyUnresolvedReferences
from PyQt5.QtGui import QIcon, QFont, QPixmap
import sys


class Gui(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # self.setGeometry(300, 300, 300, 220)

        grid = QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)
        video_item = "Video.thumb"
        names = [video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item,
                 video_item, video_item, video_item, video_item, video_item, video_item]

        positions = [(i, j) for i in range(5) for j in range(4)]

        counter = 1
        for position, name in zip(positions, names):
            if counter >= 21:
                counter = 1
            if name == '':
                continue
            button = QPushButton(name)
            filename = "{}.jpg".format(counter)
            pixmap = QPixmap(filename)
            lbl = QLabel(self)
            lbl.setPixmap(pixmap)
            grid.addWidget(lbl, *position)
            counter += 1

        # self.move(300, 150)


        # exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        # exit_action.setShortcut('Ctrl+Q')
        # exit_action.setStatusTip('Exit application')
        # exit_action.triggered.connect(qApp.quit)
        #
        # self.statusBar()
        #
        # sub_menu = QMenu('Import', self)
        # sub_action = QAction('Import mail', self)
        # sub_menu.addAction(sub_action)
        #
        # new_action = QAction('New', self)
        #
        # menubar = self.menuBar()
        # file_menu = menubar.addMenu('&File')
        # file_menu.addAction(new_action)
        # file_menu.addMenu(sub_menu)
        # file_menu.addAction(exit_action)
        #
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
        self.setWindowTitle('Sane Subscription Feed, yo!')
        self.setWindowIcon(QIcon('blu.ico'))
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

        self.show()

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

    def context_menu_vent(self, event):

        cmenu = QMenu(self)

        copy_link_action = cmenu.addAction("Copy link")
        open_link_action = cmenu.addAction("Open link")
        close_action = cmenu.addAction("Close")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == close_action:
            qApp.quit()

    def timer_event(self, e):
        if self.step >= 100:
            self.timer.stop()
            self.btn.setText('Finished')
            return

        self.step = self.step + 1
        self.pbar.setValue(self.step)

    def do_action(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn.setText('Start')
        else:
            self.timer.start(100, self)
            self.btn.setText('Stop')

    def load_progress(self):
        if self.timer.isActive():
            self.step = self.step + 1
            self.pbar.setValue(self.step)
            # self.timer.stop()
            self.btn.setText('0')
        else:
            # self.timer.start(100, self)
            self.btn.setText('1')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Gui()

    sys.exit(app.exec_())
