# !/usr/bin/python3
# -*- coding: utf-8 -*-

# PyCharm bug: PyCharm seems to be expecting the referenced module to be included in an __all__ = [] statement
from PyQt5.Qt import QClipboard
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
        self.clipboard = QApplication.clipboard()
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

        # Function menu
        func_menu = menubar.addMenu('&Function')

        # Create Function menu items
        call_func1 = QAction('Function 1', self)
        call_func2 = QAction('Function 2', self)
        call_func3 = QAction('Function 3', self)
        call_func4 = QAction('Function 4', self)
        call_func5 = QAction('Function 5', self)
        call_func6 = QAction('Function 6', self)
        call_func7 = QAction('Function 7', self)
        call_func8 = QAction('Function 8', self)
        funcs = [call_func1,call_func2,call_func3,call_func4,call_func5,call_func6,call_func7,call_func8]

        # Set function menu triggers
        call_func1.triggered.connect(self.func1)
        call_func2.triggered.connect(self.func2)
        call_func3.triggered.connect(self.func3)
        call_func4.triggered.connect(self.func4)
        call_func5.triggered.connect(self.func5)
        call_func6.triggered.connect(self.func6)
        call_func7.triggered.connect(self.func7)
        call_func8.triggered.connect(self.func8)

        counter = 1
        for func in funcs:
            # Set shortcut
            func.setShortcut('Ctrl+{}'.format(counter))

            # Add function to Function menu
            func_menu.addAction(func)
            counter += 1
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

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

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
        gv = GridView(self.subfeed, self.clipboard, self.statusBar())
        # windowLayout.addWidget(gv)
        self.setCentralWidget(gv)
        self.setLayout(windowLayout)
        self.resize(1280, 800)  # Start at a sane 16:10 minsize since thumbs are scaling now
        self.show()
        # gv.show()

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

    # def do_function(self):
    #     print("Dummy Function")

    def func1(self):
        print("Dummy Function 1")

    def func2(self):
        print("Dummy Function 2")

    def func3(self):
        print("Dummy Function 3")

    def func4(self):
        print("Dummy Function 4")

    def func5(self):
        print("Dummy Function 5")

    def func6(self):
        print("Dummy Function 6")

    def func7(self):
        print("Dummy Function 7")

    def func8(self):
        print("Dummy Function 8")


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = MainWindow()
#
#     sys.exit(app.exec_())
