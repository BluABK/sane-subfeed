import sys

from PyQt5.QtWidgets import QApplication

from timeit import default_timer

from sane_yt_subfeed.uploads import Uploads
from sane_yt_subfeed.youtube_requests import get_subscriptions, cached_authenticated_get_subscriptions
from sane_yt_subfeed.gui.main_window import MainWindow

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
    subscriptions = cached_authenticated_get_subscriptions()
    if info:
        print("Found %s subscriptions." % len(subscriptions))
    uploads = Uploads()
    subscription_feed = uploads.get_uploads(subscriptions)
    time_elsapsed = default_timer() - start
    print("\nRun time: {}".format(time_elsapsed))


