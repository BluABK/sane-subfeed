import threading

from sane_yt_subfeed.youtube.authentication import youtube_auth_keys


class GenerateKeys(threading.Thread):

    def __init__(self, keys):
        threading.Thread.__init__(self)
        self.keys = keys

    def run(self):
        self.keys.append(youtube_auth_keys())
