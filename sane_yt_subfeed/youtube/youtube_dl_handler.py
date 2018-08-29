from __future__ import unicode_literals

import datetime
import os
import threading

from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
from youtube_dl.postprocessor.ffmpeg import FFmpegPostProcessorError

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.config_handler import read_config, get_options

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
from sane_yt_subfeed.postprocessor.ffmpeg import SaneFFmpegPostProcessor, SaneFFmpegMetadataPP, SaneFFmpegMergerPP

logger = create_logger(__name__)

VIDEO_FORMATS = ['mp4', 'flv', 'ogg', 'webm', 'mkv', 'avi', 'ts']
AUDIO_MERGE_FAIL = "ERROR: Could not write header for output file #0 (incorrect codec parameters ?): Invalid argument"


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

        # logger.info("DL status == 'finished")


# FIXME: because of formating string, for channel, it can't do batch dl
class YoutubeDownload(threading.Thread):
    def __init__(self, video, threading_event, finished_listeners=None, download_progress_listener=None):
        threading.Thread.__init__(self)
        logger.debug("Created thread")
        self.video = video
        self.listeners = finished_listeners
        self.download_progress_listener = download_progress_listener
        self.threading_event = threading_event
        # FIXME: faux filename, as the application is currently not able to get final filname from youtube-dl
        # file_name = "{channel_title} - {date} - %(title)s (%(fps)s_%(vcodec)s_%(acodec)s).%(ext)s".format(
        #     channel_title=self.video.channel_title, date=self.video.date_published.strftime("%Y-%m-%d"))
        file_name = "%(uploader)s - {date} - %(title)s - _v-id-{id}.%(ext)s".format(
            date=self.video.date_published.strftime(
                "%Y-%m-%d"), id=self.video.video_id)
        self.youtube_folder = read_config('Play', 'yt_file_path', literal_eval=False)
        file_path = os.path.join(self.youtube_folder, file_name)

        self.proxies = []
        for proxy_option in get_options('Youtube-dl_proxies'):
            this_proxy_option = read_config('Youtube-dl_proxies', proxy_option, literal_eval=False).strip('"').strip(
                "'")
            if this_proxy_option is not "" and this_proxy_option is not None:
                self.proxies.append(this_proxy_option)

        self.ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
            'outtmpl': file_path,
            'forcefilename': 'True'
        }
        self.add_userconfig_opts(self.ydl_opts)

        self.proxy_ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
            'outtmpl': file_path,
            'forcefilename': 'True',
            'proxy': None
        }
        self.add_userconfig_opts(self.proxy_ydl_opts)

    def add_userconfig_opts(self, ydl_opts):
        logger.info("Adding custom user youtube-dl opts (if any)")

        for option in get_options('Youtube-dl_opts'):
            value = read_config('Youtube-dl_opts', option)
            if value is True or value is False:
                value = str(value)

            logger.info("Setting option: {} = {}".format(option, value))
            ydl_opts[option] = value

        logger.debug("Final ydl_opts dict after adding user options: {}".format(ydl_opts))

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

    def embed_metadata(self):
        """
        Embeds metadata tags (and optionally remaps them) to media files
        :return:
        """

        if read_config('Postprocessing', 'embed_metadata', literal_eval=True) is not True:
            logger.debug("Skipping disabled metadata embedding operation")
            return

        literal_eval = False
        # if read_config('Postprocessing', 'remap_tags', literal_eval=True):
        #     logger.info("Embedding metadata with remapped tags")
        #     custom_map = [
        #         (read_config('Postprocessing', 'map_title', literal_eval=literal_eval), ('track', 'title')),
        #         (read_config('Postprocessing', 'map_date', literal_eval=literal_eval), 'upload_date'),
        #         ((read_config('Postprocessing', 'map_description', literal_eval=literal_eval),
        #           read_config('Postprocessing', 'map_comment', literal_eval=literal_eval)), 'description'),
        #         (read_config('Postprocessing', 'map_purl', literal_eval=literal_eval), 'webpage_url'),
        #         (read_config('Postprocessing', 'map_track', literal_eval=literal_eval), 'track_number'),
        #         (read_config('Postprocessing', 'map_artist', literal_eval=literal_eval),
        #          ('artist', 'creator', 'uploader', 'uploader_id')),
        #         (read_config('Postprocessing', 'map_genre', literal_eval=literal_eval)),
        #         (read_config('Postprocessing', 'map_album', literal_eval=literal_eval)),
        #         (read_config('Postprocessing', 'map_album_artist', literal_eval=literal_eval)),
        #         (read_config('Postprocessing', 'map_disc', literal_eval=literal_eval), 'disc_number')]
        # else:

        logger.info("Embedding metadata with default tags")
        # Keys are media metadata tag names (https://wiki.multimedia.cx/index.php?title=FFmpeg_Metadata)
        # FIXME: Add other presets like music
        # Video as TV-series preset
        info = {'not_a_tag': ['not_a_tag', 'filepath', 'ext'],
                'filepath': self.video.vid_path,
                'ext': self.video.vid_path.split('.')[-1],
                # 'ext': read_config('Youtube-dl_opts', 'merge_output_format', literal_eval=False),
                'title': self.video.title,
                'show': self.video.channel_title,
                'date': self.video.date_published.isoformat(),
                'purl': self.video.url_video,
                'network': 'YouTube',
                ('description', 'comment', 'synopsis'): self.video.description}
        logger.debug(info)
        SaneFFmpegMetadataPP(SaneFFmpegPostProcessor()).run(info)

    def run(self):
        logger.debug("Started download thread")
        self.threading_event.wait()
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
        except FFmpegPostProcessorError as horrible_ffmpeg_death:
            if horrible_ffmpeg_death.msg == AUDIO_MERGE_FAIL:
                logger.warning("Handling incompatible container audio and video stream muxing")
                # FIXME: Reacquire filename and formats so they can be sent to SaneFFmpegMergerPP
                simulated_opts = self.ydl_opts
                simulated_opts['simulate'] = 'True'
                # simulated_opts
                with YoutubeDL(self.ydl_opts) as ydl:
                    logger.info("Simulating download for: {} - {} [{}]".format(self.video.channel_title,
                                                                               self.video.title,
                                                                               self.video.url_video))
                    ydl.download([self.video.url_video])
                reconstruct_dataset = None
                videofile = None
                audiofile = None
                info = {'__files_to_merge': [videofile, audiofile]}
                SaneFFmpegMergerPP(SaneFFmpegPostProcessor()).run(info, encode_audio='libvo_aacenc')

        except Exception as e:
            logger.exception(e)
            pass

        logger.info("Finished downloading: {} - {} [{}]".format(self.video.channel_title, self.video.title,
                                                                self.video.url_video))

        for name in os.listdir(self.youtube_folder):
            if self.video.video_id in name and name.split('.')[-1] in VIDEO_FORMATS:
                self.video.vid_path = os.path.join(self.youtube_folder, name)

        self.video.date_downloaded = datetime.datetime.utcnow()

        # Embed metadata (optional)
        self.embed_metadata()

        self.download_progress_listener.finishedDownload.emit()
        if self.listeners:
            for listener in self.listeners:
                listener.emit(self.video)

    def my_hook(self, event):
        self.download_progress_listener.updateProgress.emit(event)
        self.threading_event.wait()
