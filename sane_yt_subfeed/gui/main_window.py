# !/usr/bin/python3
# -*- coding: utf-8 -*-

# PyCharm bug: PyCharm seems to be expecting the referenced module to be included in an __all__ = [] statement

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, \
    QMenu, QProgressBar, QVBoxLayout
from PyQt5.QtGui import QIcon

from sane_yt_subfeed.thumbnail_handler import thumbnails_dl_and_paths
from sane_yt_subfeed.uploads import Uploads
from sane_yt_subfeed.gui.views.grid_view import GridView


class MainWindow(QMainWindow):
    uploads = None
    gv = None

    def __init__(self):
        super().__init__()
        # self.subfeed = subfeed
        self.uploads = Uploads()
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
        dump_urls = QAction('Copy all URLs', self)
        call_func2 = QAction('Function 2', self)
        call_func3 = QAction('Function 3', self)
        call_func4 = QAction('Function 4', self)
        call_func5 = QAction('Function 5', self)
        call_func6 = QAction('Function 6', self)
        call_func7 = QAction('Function 7', self)
        refresh_list = QAction('Refresh Feed', self)
        funcs = [call_func2,call_func3,call_func4,call_func5,call_func6,call_func7]

        # Set function menu triggers
        dump_urls.triggered.connect(self.dump_urls_clpbd)
        dump_urls.setStatusTip('Copy URLs of all currently visible videos to clipboard')
        func_menu.addAction(dump_urls)
        dump_urls.setShortcut('Ctrl+D')
        call_func2.triggered.connect(self.func2)
        call_func3.triggered.connect(self.func3)
        call_func4.triggered.connect(self.func4)
        call_func5.triggered.connect(self.func5)
        call_func6.triggered.connect(self.func6)
        call_func7.triggered.connect(self.func7)
        refresh_list.triggered.connect(self.refresh_list)

        counter = 2
        for func in funcs:
            # Set shortcut
            func.setShortcut('Ctrl+{}'.format(counter))

            # Set status_bar on-hover message for func
            func.setStatusTip('Execute Function {}'.format(counter))

            # Add function to Function menu
            func_menu.addAction(func)
            counter += 1

        # refresh_list
        refresh_list.setShortcut('Ctrl+R')
        refresh_list.setStatusTip('Execute Function {}'.format(counter))
        func_menu.addAction(refresh_list)



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
        self.gv = GridView(self.uploads, self.clipboard, self.statusBar())
        # print(grid)
        # windowLayout.addWidget(gv)
        self.setCentralWidget(self.gv)
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

    def dump_urls_clpbd(self):
        """
        Adds the url of each video in the view to a string, separated by \n and puts it on clipboard.
        :return:
        """
        grid_items = 20
        urls = ""
        for i in range(grid_items):
            urls += "{}\n".format(self.gv.uploads.uploads[i].url_video)

        print("Copied URLs to clipboard: \n{}".format(urls))
        self.clipboard.setText(urls)
        self.statusBar().showMessage('Copied {} URLs to clipboard'.format(len(urls.splitlines())))

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

    def refresh_list(self):
        self.gv.uploads.get_uploads()
        uploads = self.gv.uploads.uploads[:30]
        thumbnails_dl_and_paths(self.gv.uploads.uploads[:30])
        for q_label, video in zip(self.gv.q_labels, uploads):
            q_label.set_video(video)
            q_label.update()
