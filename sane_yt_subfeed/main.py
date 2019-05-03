import datetime
import threading

from sane_yt_subfeed.settings import mutable_settings
from sane_yt_subfeed.controller.controller import Controller
from sane_yt_subfeed.database.models import Test
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.youtube.update_videos import refresh_uploads, load_keys
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions, list_uploaded_videos_search, \
    list_uploaded_videos_page

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)

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
    # Used by backend to determine whether or not application is using GUI
    mutable_settings.using_gui = True
    controller = Controller()
    controller.run()


def run_with_cli():
    logger.info('Running with CLI')
    logger.error("CLI UI Not yet implemented")
    exit(0)


def cli_refresh_and_print_subfeed():
    logger.info('Running with print/console')
    new_videos = refresh_uploads()
    for vid in new_videos:
        print(vid)


# FIXME: move this method to the youtube package
def run_channels_test():
    logger.info('Running Channels Test')
    subscriptions = get_subscriptions(cached_subs)
    youtube_keys = load_keys(len(subscriptions))
    test_threads = []
    results = []
    logger.info("Channels Test: Starting miss and pages tests")
    for subscription, youtube_key in (subscriptions, youtube_keys):
        test = RunTestsThreaded(subscription, youtube_key, results)
        test.start()
        test_threads.append(test)

    logger.info("Channels Test: Waiting for test threads")
    for thread in test_threads:
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
        """
        threading.Thread.__init__(self)
        self.subscription = subscription
        self.youtube_key = youtube_key
        self.results = results

    # TODO: Handle failed requests
    def run(self):
        search_videos = []
        list_uploaded_videos_search(self.youtube_key, self.subscription.id, search_videos, 2)
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

        result = [datetime.datetime.utcnow(), test_pages, test_miss, self.subscription]
        self.results.append(result)
