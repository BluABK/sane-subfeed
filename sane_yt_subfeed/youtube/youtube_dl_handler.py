from __future__ import unicode_literals

import datetime
import os
import threading
import time
import re

from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError, DownloadError

from sane_yt_subfeed.config_handler import read_config, get_options

from sane_yt_subfeed import create_logger

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def my_hook(d):
    time.sleep(0.01)
    if d['status'] == 'finished':
        pass
        # logger.info("DL status == 'finished")


# FIXME: because of formating string, for channel, it can't do batch dl
class YoutubeDownload(threading.Thread):
    def __init__(self, video, finished_listener=None):
        threading.Thread.__init__(self)
        logger.debug("Created thread")
        self.video = video
        self.listener = finished_listener
        # FIXME: faux filename, as the application is currently not able to get final filname from youtube-dl
        # file_name = "{channel_title} - {date} - %(title)s (%(fps)s_%(vcodec)s_%(acodec)s).%(ext)s".format(
        #     channel_title=self.video.channel_title, date=self.video.date_published.strftime("%Y-%m-%d"))
        file_name = "%(uploader)s - {date} - %(title)s - _v-id-{id}.%(ext)s".format(
            date=self.video.date_published.strftime(
                "%Y-%m-%d"), id=self.video.video_id)
        # file_name = 'testwsefefewf.fwef'
        self.youtube_folder = read_config('Play', 'yt_file_path', literal_eval=False)
        file_path = os.path.join(self.youtube_folder, file_name)

        self.proxies = []
        for proxy_option in get_options('Youtube-dl_proxies'):
            this_proxy_option = read_config('Youtube-dl_proxies', proxy_option, literal_eval=False).strip('"').strip("'")
            if this_proxy_option is not "" and this_proxy_option is not None:
                self.proxies.append(this_proxy_option)

        self.ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'outtmpl': file_path,
            'forcefilename': 'True'
        }

        self.proxy_ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'outtmpl': file_path,
            'forcefilename': 'True',
            'proxy': None
        }

    def download_with_proxy(self):
        """
        Download a video using a proxy, returns True if a proxy succeeded.
        :return:
        """
        if len(self.proxies) <= 0:
            logger.warning("Attempted to download using proxy, but no proxies are defined!")
            return False

        for proxy in self.proxies:
            try:
                self.proxy_ydl_opts['proxy'] = proxy
                logger.info(
                    "Video '{}' is geo blocked, retrying with proxy: {}.".format(self.video.title, proxy))

                with YoutubeDL(self.proxy_ydl_opts) as ydl:
                    logger.info(
                        "Starting download (proxy: {}) for: {} - {} [{}]".format(proxy, self.video.channel_title,
                                                                                 self.video.title,
                                                                                 self.video.url_video))
                    ydl.download([self.video.url_video])
                    return True
            except DownloadError as dl_exc:
                logger.warning(
                    "Proxy {} download of geo blocked video '{}' failed.".format(proxy, self.video.title))
                logger.exception(dl_exc)
                pass

        return False

    def run(self):
        logger.debug("Started download thread")
        # url_list = []
        # for video in self.videos:
        #     url_list.append(video.url_video)
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                logger.info("Starting download for: {} - {} [{}]".format(self.video.channel_title, self.video.title,
                                                                         self.video.url_video))
                ydl.download([self.video.url_video])
        except DownloadError as dl_exc:
            if str(dl_exc) == "ERROR: The uploader has not made this video available in your country." or \
                    ("ERROR:" in str(dl_exc) and "blocked it in your country" in str(dl_exc)):
                if self.download_with_proxy() is not True:
                    logger.error("All proxies have failed to download geo blocked video '{}'!".format(self.video.title))
                    logger.exception(dl_exc)
                pass
            else:
                logger.exception(dl_exc)
                pass
        except Exception as e:
            logger.exception(e)
            pass

        logger.info("Finished downloading: {} - {} [{}]".format(self.video.channel_title, self.video.title,
                                                                self.video.url_video))

        for name in os.listdir(self.youtube_folder):
            if self.video.video_id in name:
                self.video.vid_path = os.path.join(self.youtube_folder, name)

        if self.listener:
            self.video.date_downloaded = datetime.datetime.utcnow()
            self.listener.emit(self.video)
