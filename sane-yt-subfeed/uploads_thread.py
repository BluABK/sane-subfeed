import threading

from youtube_requests import list_uploaded_videos_search


class GetUploadsThread(threading.Thread):

    def __init__(self, thread_id, youtube, channel, search_pages, info=False, debug=False):
        """
        Init GetUploadsThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.channel = channel
        self.info = info
        self.debug = debug
        self.statistics = {}
        self.videos = []
        self.job_done = False
        self.youtube = youtube
        self.search_pages = search_pages

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        channel_title = self.channel['snippet']['title']
        channel_id = self.channel['snippet']['resourceId']['channelId']
        if self.debug:
            print("Starting #%s for channel: %s" % (self.thread_id, channel_title), end='')
            if self.info:
                print(" -- Fetching Uploaded videos for channel: %s" % channel_title)
            print("")

        # youtube = youtube_auth_keys()

        # self.videos = get_channel_uploads(self.youtube, channel_id)
        self.videos = list_uploaded_videos_search(self.youtube, channel_id, self.search_pages)

        self.job_done = True
        if self.debug:
            print("Exiting #%s" % self.thread_id)

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
