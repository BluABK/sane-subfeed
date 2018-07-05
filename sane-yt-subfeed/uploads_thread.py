import threading


class GetUploadsThread(threading.Thread):

    def __init__(self, uploads, thread_id, channel, info=False, debug=False):
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
        self.uploads = uploads

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        channel_title = self.channel['snippet']['title']
        channel_id = self.channel['snippet']['resourceId']['channelId']
        print("Starting #%s for channel: %s" % (self.thread_id, channel_title), end='')
        if self.info:
            print(" -- Fetching Uploaded videos for channel: %s" % channel_title)
        else:
            print("")
        retval = self.uploads.get_channel_uploads(channel_id)

        self.videos = retval[0]
        self.statistics = retval[1]

        self.job_done = True
        print("Exiting #%s" % self.thread_id)

    def get_videos(self):
        """
        Return a list of videos
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
