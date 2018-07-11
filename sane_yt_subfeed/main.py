import datetime
import sys
import time

from PyQt5.QtWidgets import QApplication

from timeit import default_timer

from tqdm import tqdm

from sane_yt_subfeed.database.models import Test
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.gui.main_window import MainWindow
from sane_yt_subfeed.youtube.update_videos import refresh_uploads, load_keys
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions, list_uploaded_videos, \
    list_uploaded_videos_search, list_uploaded_videos_page

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


def run_channels_test():
    subscriptions = get_subscriptions(cached_subs)
    youtube_keys = load_keys(subscriptions)
    for subscription, youtube_key in tqdm(zip(subscriptions, youtube_keys),
                                          desc="Testing channels with playlistItem and search",
                                          total=len(subscriptions)):
        search_videos = []
        list_uploaded_videos_search(youtube_key, subscription.id, search_videos, 2, live_videos=False)
        playlist_videos = []
        next_page = list_uploaded_videos_page(youtube_key, playlist_videos, subscription.playlist_id)

        test_miss = 0
        for search_video in search_videos:
            in_playlist = False
            for playlist_video in playlist_videos:
                if playlist_video.video_id == search_video.video_id:
                    in_playlist = True
                    test_miss += 1
                    break
            if not in_playlist:
                break

        test_pages = 0
        hits = 0
        search_video_pointer = 0
        while hits < 50:
            for search_video_index in range(search_video_pointer, 99):
                in_playlist = False
                for playlist_video in playlist_videos:
                    if len(search_videos) > (search_video_index + 1):
                        if playlist_video.video_id == search_videos[search_video_pointer].video_id:
                            in_playlist = True
                            search_video_pointer += 1
                            hits += 1
                            break
                    else:
                        hits = 100
                        test_pages = 1
                        break
                if not in_playlist:
                    break
            test_pages += 1
            if test_pages > 30:
                break
            next_page = list_uploaded_videos_page(youtube_key, playlist_videos, subscription.playlist_id,
                                                  playlistitems_list_request=next_page)
        db_session.add(Test(datetime.datetime.now(), test_pages, test_miss, subscription))
        db_session.commit()
