import sys

from PyQt5.QtWidgets import QApplication

from timeit import default_timer

from sane_yt_subfeed.gui.main_window import MainWindow
from sane_yt_subfeed.youtube.update_videos import refresh_uploads

cached_subs = True
global_debug = False
global_info = False
info = True
debug = True
print_statistics = True


# Auth OAuth2 with YouTube API

# Create controller object

def run_with_gui():
    app = QApplication(sys.argv)
    ex = MainWindow()
    # ex = GridView(subscription_feed[:20])
    app.exec_()


def run_print():
    start = default_timer()
    refresh_uploads()
    time_elsapsed = default_timer() - start
    print("\nRun time: {}".format(time_elsapsed))



