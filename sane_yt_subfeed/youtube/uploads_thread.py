import threading
import timeit

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.youtube.youtube_requests import list_uploaded_videos_search, get_channel_uploads, \
    list_uploaded_videos
from sane_yt_subfeed.log_handler import logger


class GetUploadsThread(threading.Thread):

    def __init__(self, thread_id, youtube, channel_id, playlist_id, videos, list_pages, search_pages,
                 deep_search=False):
        """
        Init GetUploadsThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        threading.Thread.__init__(self)
        self.videos = videos
        self.thread_id = thread_id
        self.job_done = False
        self.youtube = youtube
        self.search_pages = search_pages
        self.list_pages = list_pages
        self.channel_id = channel_id
        self.playlist_id = playlist_id
        self.deep_search = deep_search

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """

        # youtube = youtube_auth_keys()

        # self.videos = get_channel_uploads(self.youtube, channel_id)
        use_tests = read_config('Requests', 'use_tests')

        if self.deep_search:
            temp_videos = []
            list_uploaded_videos_search(self.youtube, self.channel_id, temp_videos, self.search_pages)
            list_uploaded_videos(self.youtube, temp_videos, self.playlist_id, self.list_pages)
            self.merge_same_videos_in_list(temp_videos)
            self.videos.extend(temp_videos)

        elif use_tests:
            channel = db_session.query(Channel).get(self.channel_id)
            miss = read_config('Requests', 'miss_limit')
            pages = read_config('Requests', 'test_pages')
            extra_pages = read_config('Requests', 'extra_list_pages')
            list_pages = 0
            temp_videos = []
            for test in channel.tests:
                if test.test_pages > list_pages:
                    list_pages = test.test_pages
                if test.test_miss < miss or test.test_pages > pages:
                    db_session.remove()
                    list_uploaded_videos_search(self.youtube, self.channel_id, temp_videos, self.search_pages)
                    break
            db_session.remove()
            list_uploaded_videos(self.youtube, temp_videos, self.playlist_id,
                                 min(pages + extra_pages, list_pages + extra_pages))
            self.merge_same_videos_in_list(temp_videos)
            self.videos.extend(temp_videos)

        else:
            use_playlist_items = read_config('Debug', 'use_playlistItems')
            if use_playlist_items:
                list_uploaded_videos(self.youtube, self.videos, self.playlist_id, self.list_pages)
            else:
                list_uploaded_videos_search(self.youtube, self.channel_id, self.videos, self.search_pages)

        self.job_done = True

    @staticmethod
    def merge_same_videos_in_list(videos):

        # start_time = timeit.default_timer()
        for commpare_vid in videos:
            for vid in videos:
                # FIXME: wasteful compare
                if commpare_vid != vid and commpare_vid.video_id == vid.video_id:
                    # FIXME: check if grab method is in list?
                    commpare_vid.grab_methods.extend(vid.grab_methods)
                    videos.remove(vid)
        # print(timeit.default_timer() - start_time)

    def get_videos(self):
        """
        Return a list of Video objects
        :return:
        """
        return self.videos

    def get_id(self):
        """
        Return ID of this thread
        :return:
        """
        return self.thread_id

    def finished(self):
        """
        Return a boolean to check if run() has ended.
        :return:
        """
        return self.job_done
