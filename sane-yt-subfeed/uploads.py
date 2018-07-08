import threading

from authentication import youtube_auth_keys
from generate_keys import GenerateKeys
from pickle_handler import load_batch_build_key, dump_batch_build_key
from uploads_thread import GetUploadsThread
import time
from collections import OrderedDict
from tqdm import tqdm  # fancy progress bar

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
        else:
            uploads = self.get_uploads_threaded()
        self.uploads = uploads
        return uploads

    def get_uploads_threaded(self):
        """
        Returns a date-sorted list of each subscription's "Uploaded videos" playlist.
        :return:
        """
        statistics = []
        videos = []

        thread_increment = 0
        thread_list = []
        delay = self.load_time / len(self.subs)  # TODO: Implement or drop

        youtube_list = []
        try:
            youtube_list = load_batch_build_key()
        except FileNotFoundError:
            print("\nGenerating youtube key builds:")
            youtube_list.extend(self.generate_keys(len(self.subs)))
            dump_batch_build_key(youtube_list)

        diff = len(self.subs) - len(youtube_list)
        if diff > 0:
            print("\nGenerating diff youtube key builds:")
            youtube_list.extend(self.generate_keys(diff))
            dump_batch_build_key(youtube_list)

        print("Creating YouTube service object from API_KEY for %s channels:" % len(self.subs))
        # thread_limit = 1
        for channel, youtube in tqdm(zip(self.subs, youtube_list)):
            if self.debug:
                print("Creating YouTube service object from API_KEY for channel: %s" % channel['snippet']['title'])
            thread = GetUploadsThread(thread_increment, youtube, channel, 1, debug=False)
            thread_list.append(thread)
            thread_increment += 1
            # if thread_increment >= thread_limit:
            #     break
        print("\nStarting threads:")
        for t in tqdm(thread_list):
            t.start()

        print("\nCollecting data from %s threads:" % len(thread_list))
        for t in tqdm(thread_list):
            t.join()
            videos.extend(t.get_videos())

        # return OrderedDict(sorted(videos.items(), reverse=True))
        return sorted(videos, key=lambda video: video.date_published, reverse=True)

    @staticmethod
    def generate_keys(key_number):
        keys = []
        threads = []

        print("\nStarting key generation threads:")
        for _ in tqdm(range(key_number)):
            t = GenerateKeys(keys)
            t.start()
            threads.append(t)

        print("\nClosing key generation threads:")
        for t in tqdm(threads):
            t.join()
        return keys
