from uploads_thread import GetUploadsThread
import time
from collections import OrderedDict
from tqdm import tqdm   # fancy progress bar

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO


class Uploads:
    subs = None
    debug = False
    info = False
    disable_threading = False
    uploads = None
    limit = 25
    youtube = None
    load_time = 30

    def __init__(self):
        pass

    def get_uploads(self, subs, debug=False, info=False, load_time=30, disable_threading=False, limit=25):
        self.subs = subs
        self.debug = debug
        self.info = info
        self.load_time = load_time
        self.disable_threading = disable_threading
        self.limit = limit
        if disable_threading:
            raise ValueError('Disable threading is obsolete')
            # uploads = self.get_uploads_sequential()
        else:
            uploads = self.get_uploads_threaded()
        self.uploads = uploads
        return uploads

    # def get_uploads_sequential(self):
    #     new_videos_by_timestamp = {}
    #
    #     for channel in self.subs:
    #         channel_title = channel['snippet']['title']
    #         channel_id = channel['snippet']['resourceId']['channelId']
    #         if self.info:
    #             print("Fetching Uploaded videos for channel: %s" % channel_title)
    #
    #         # Create a (datestamp: video) dict
    #         for video in self.get_channel_uploads(channel_id):
    #             new_videos_by_timestamp.update({video.date_published: video})
    #
    #     # Return a reverse chronological sorted OrderedDict (newest --> oldest)
    #     return OrderedDict(sorted(new_videos_by_timestamp.items(), reverse=True))

    def get_uploads_threaded(self):
        """
        Returns a date-sorted OrderedDict of a list of each subscriptions' "Uploaded videos" playlist.
        :return:
        """
        statistics = []
        new_videos_by_timestamp = {}

        thread_increment = 0
        thread_list = []
        delay = self.load_time / len(self.subs)     # TODO: Implement or drop

        print("Creating YouTube service object from API_KEY for %s channels:" % len(self.subs))
        for channel in tqdm(self.subs):
            if self.debug:
                print("Creating YouTube service object from API_KEY for channel: %s" % channel['snippet']['title'])
            thread = GetUploadsThread(thread_increment, channel,  debug=False)
            thread_list.append(thread)
            thread_increment += 1

        print("\nStarting threads:")
        for t in tqdm(thread_list):
            t.start()
            # time.sleep(delay)
            # time.sleep(0.001)

        print("\nCollecting data from %s threads:" % len(thread_list))
        for t in tqdm(thread_list):
            while t.finished() is not True:
                if self.debug:
                    print("\nNOTE: Thread #%s is still not done... Sleeping for 0.010 seconds" % t.get_id())
                time.sleep(0.010)
            for vid in t.get_videos():
                new_videos_by_timestamp.update({vid.date_published: vid})

        return OrderedDict(sorted(new_videos_by_timestamp.items(), reverse=True))
