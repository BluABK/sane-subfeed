import threading

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.youtube.youtube_requests import list_uploaded_videos_search, get_channel_uploads, \
    list_uploaded_videos
from sane_yt_subfeed.log_handler import logger


class GetUploadsThread(threading.Thread):

    def __init__(self, thread_id, youtube, channel_id, playlist_id, videos, req_limit):
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
        self.req_limit = req_limit
        self.channel_id = channel_id
        self.playlist_id = playlist_id

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """

        # youtube = youtube_auth_keys()

        # self.videos = get_channel_uploads(self.youtube, channel_id)

        use_tests = read_config('Requests', 'use_tests')
        if use_tests:
            channel = db_session.query(Channel).get(self.channel_id)
            miss = read_config('Requests', 'miss_limit')
            pages = read_config('Requests', 'test_pages')
            extra_pages = read_config('Requests', 'extra_list_pages')
            used_list = False
            list_pages = 0
            for test in channel.tests:
                if test.test_pages > list_pages:
                    list_pages = test.test_pages
                if test.test_miss < miss or test.test_pages > pages:
                    used_list = True
                    db_session.remove()
                    list_uploaded_videos_search(self.youtube, self.channel_id, self.videos, self.req_limit)
                    break
            if not used_list:
                list_uploaded_videos(self.youtube, self.videos, self.playlist_id, list_pages+extra_pages)
                db_session.remove()
        else:
            use_playlist_items = read_config('Debug', 'use_playlistItems')
            if use_playlist_items:
                list_uploaded_videos(self.youtube, self.videos, self.playlist_id, self.req_limit)
            else:
                list_uploaded_videos_search(self.youtube, self.channel_id, self.videos, self.req_limit)

        self.job_done = True

    def get_videos(self):
        """
        Return a list of Video objects
        :return:
        """
        return self.videos

    def get_statistics(self):
        """
        Return a dict of statistics/timings
        :return:
        """
        return self.statistics

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
