import datetime
import sys
import threading
import time

from PyQt5.QtWidgets import QApplication

from timeit import default_timer

from tqdm import tqdm

from sane_yt_subfeed.controller.controller import Controller
from sane_yt_subfeed.database.models import Test
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.gui.main_window import MainWindow
from sane_yt_subfeed.youtube.update_videos import refresh_uploads, load_keys
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions, list_uploaded_videos, \
    list_uploaded_videos_search, list_uploaded_videos_page
from sane_yt_subfeed.log_handler import logger

cached_subs = True
global_debug = False
global_info = False
info = True
debug = True
print_statistics = True


# Auth OAuth2 with YouTube API

# Create controller object

def run_with_gui():
    logger.info('Running with GUI')
    controller = Controller()
    controller.run()


def run_print():
    start = default_timer()
    refresh_uploads()
    time_elsapsed = default_timer() - start
    print("\nRun time: {}".format(time_elsapsed))


# FIXME: move this method to the youtube package
def run_channels_test():
    logger.info('Running Channels test')
    subscriptions = get_subscriptions(cached_subs)
    youtube_keys = load_keys(subscriptions)
    test_threads = []
    results = []
    for subscription, youtube_key in tqdm(zip(subscriptions, youtube_keys),
                                          desc="Starting miss and pages tests",
                                          total=len(subscriptions)):
        test = RunTestsThreaded(subscription, youtube_key, results)
        test.start()
        test_threads.append(test)
    for thread in tqdm(test_threads, desc="Waiting for test threads"):
        thread.join()

    for result in results:
        test = Test(result[0], result[1], result[2], result[3])
        db_session.add(test)
    db_session.commit()
    db_session.remove()


class RunTestsThreaded(threading.Thread):

    def __init__(self, subscription, youtube_key, results):
        """
        Init GetUploadsThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        threading.Thread.__init__(self)
        self.subscription = subscription
        self.youtube_key = youtube_key
        self.results = results

    # TODO: Handle failed requests
    def run(self):
        search_videos = []
        list_uploaded_videos_search(self.youtube_key, self.subscription.id, search_videos, 2, live_videos=False)
        playlist_videos = []
        next_page = list_uploaded_videos_page(self.youtube_key, playlist_videos, self.subscription.playlist_id)

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
            next_page = list_uploaded_videos_page(self.youtube_key, playlist_videos, self.subscription.playlist_id,
                                                  playlistitems_list_request=next_page)

        result = [datetime.datetime.now(), test_pages, test_miss, self.subscription]
        self.results.append(result)

