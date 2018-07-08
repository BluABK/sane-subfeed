# !/usr/bin/python3
# -*- coding: utf-8 -*-

# PyCharm bug: PyCharm seems to be expecting the referenced module to be included in an __all__ = [] statement
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QBasicTimer
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QAction, qApp, \
    QMenu, QGridLayout, QProgressBar, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QIcon, QFont, QPixmap
import sys


from .grid_view import GridView


class MainWindow(QMainWindow):
    subfeed = None

    def __init__(self, subfeed):
        super().__init__()
        self.subfeed = subfeed
        self.init_ui()

    def init_ui(self):
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)
        #
        self.statusBar()
        #
        sub_menu = QMenu('Import', self)
        sub_action = QAction('Import mail', self)
        sub_menu.addAction(sub_action)
        #
        new_action = QAction('New', self)
        #
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new_action)
        file_menu.addMenu(sub_menu)
        file_menu.addAction(exit_action)
        #
        QToolTip.setFont(QFont('SansSerif', 10))
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
        self.statusBar().showMessage('Ready.')

        # self.a
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

        windowLayout = QVBoxLayout()
        gv = GridView(self.subfeed)
        # windowLayout.addWidget(gv)
        self.setCentralWidget(gv)
        self.setLayout(windowLayout)
        self.resize(1280, 800)  # Start at a sane 16:10 minsize since thumbs are scaling now
        self.show()
        # gv.show()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = MainWindow()
#
#     sys.exit(app.exec_())
