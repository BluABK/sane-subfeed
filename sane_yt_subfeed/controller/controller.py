import sys
import threading
import time

# FIXME: imp*
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication

# FIXME: imp*
from sane_yt_subfeed.controller.listeners import *
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.gui.main_window import MainWindow


class Controller:

    def __init__(self):
        super().__init__()
        # self.grid_view_listener = GridViewListener(self)
        # self.thread = QThread()
        # self.thread.start()
        # self.grid_view_listener.moveToThread(self.thread)


    def run(self):
        # thread = QThread
        # thread.start()
        # while True:
        #     time.sleep(0.5)
        model = MainModel([], [], [])

        app = QApplication(sys.argv)
        window = MainWindow(model)
        window.show()
        app.exec_()

