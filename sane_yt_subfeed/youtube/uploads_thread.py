import threading

from sane_yt_subfeed.youtube.youtube_requests import list_uploaded_videos_search


class GetUploadsThread(threading.Thread):

    def __init__(self, thread_id, youtube, channel_id, videos, search_pages):
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
        self.channel_id = channel_id

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """

        # youtube = youtube_auth_keys()

        # self.videos = get_channel_uploads(self.youtube, channel_id)
        self.videos = list_uploaded_videos_search(self.youtube, self.channel_id, self.videos, self.search_pages)

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
