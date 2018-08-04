from __future__ import unicode_literals

import datetime
import os
import threading
import time
import re

from youtube_dl import YoutubeDL

from sane_yt_subfeed.config_handler import read_config


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    time.sleep(0.01)
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


# FIXME: because of formating string, for channel, it can't do batch dl
class YoutubeDownload(threading.Thread):
    def __init__(self, video, finished_listener=None):
        threading.Thread.__init__(self)
        self.video = video
        self.listener = finished_listener
        # FIXME: faux filename, as the application is currently not able to get final filname from youtube-dl
        # file_name = "{channel_title} - {date} - %(title)s (%(fps)s_%(vcodec)s_%(acodec)s).%(ext)s".format(
        #     channel_title=self.video.channel_title, date=self.video.date_published.strftime("%Y-%m-%d"))
        file_name = "%(uploader)s - {date} - %(title)s - _v-id-{id}.%(ext)s".format(date=self.video.date_published.strftime(
                                                                             "%Y-%m-%d"), id=self.video.video_id)
        # file_name = 'testwsefefewf.fwef'
        self.youtube_folder = read_config('Play', 'yt_file_path', literal_eval=False)
        file_path = os.path.join(self.youtube_folder, file_name)

        self.ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'outtmpl': file_path,
            'forcefilename': 'True'
        }

    def run(self):
        # url_list = []
        # for video in self.videos:
        #     url_list.append(video.url_video)
        with YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.video.url_video])

        for name in os.listdir(self.youtube_folder):
            if self.video.video_id in name:
                self.video.vid_path = os.path.join(self.youtube_folder, name)

        if self.listener:
            self.video.date_downloaded = datetime.datetime.utcnow()
            self.listener.emit(self.video)
