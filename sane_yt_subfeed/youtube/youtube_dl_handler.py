from __future__ import unicode_literals

import threading

from youtube_dl import YoutubeDL


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


class YoutubeDownload(threading.Thread):
    def __init__(self, videos):
        threading.Thread.__init__(self)
        self.videos = videos

    def run(self):
        url_list = []
        for video in self.videos:
            url_list.append(video.url_video)

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(url_list)
