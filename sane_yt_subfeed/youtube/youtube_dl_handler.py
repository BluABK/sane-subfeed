from __future__ import unicode_literals

import datetime
import os
import threading

from sane_yt_subfeed.handlers.config_handler import read_config, get_options, get_valid_options
from sane_yt_subfeed import create_logger
# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)
try:
    YOUTUBE_DL_AVAILABLE = True
    from youtube_dl import YoutubeDL
    from youtube_dl.utils import DownloadError
    from sane_yt_subfeed.postprocessor.ffmpeg import \
        SaneFFmpegPostProcessor, SaneFFmpegMetadataPP, SaneFFmpegMergerPP, SaneFFmpegPostProcessorError

except ModuleNotFoundError as module_exc:
    YOUTUBE_DL_AVAILABLE = False


VIDEO_FORMATS = ['mp4', 'flv', 'ogg', 'webm', 'mkv', 'avi', 'ts']
AUDIO_MERGE_FAILS = ["Could not write header for output file #0 (incorrect codec parameters ?): Invalid argument",
                     "ERROR: Could not write header for output file #0 (incorrect codec parameters ?): Invalid argument"
                     ]
IO_ERROR = ["ERROR: unable to write data: [Errno 5] Input/output error"]
WRITE_DENIED_ERROR = ["ERROR: unable to open for writing: [Errno 13] Permission denied"]
VIDEO_IS_GEOBLOCKED_ERRORS = ["The uploader has not made this video available in your country.",
                              "blocked it in your country",
                              "This video is not available."]
SSL_HANDSHAKE_FAILS = ["ERROR: Unable to download webpage: <urlopen error [Errno 0] Error> "
                       "(caused by URLError(OSError(0, 'Error')))",
                       "ERROR: unable to download video data: <urlopen error [Errno 0] Error>",
                       "<urlopen error [Errno 0] Error>"]

DOWNLOAD_RUNNING = 0
DOWNLOAD_FINISHED = 1
DOWNLOAD_PAUSED = 2
DOWNLOAD_FAILED = 3


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


# FIXME: because of formating string, for channel, it can't do batch dl
class YoutubeDownload(threading.Thread):
    def __init__(self, video, threading_event, finished_listeners=None, download_progress_listener=None):
        if not YOUTUBE_DL_AVAILABLE:
            logger.error("Youtube-DL handler was called, but no youtube_dl module exists, aborting init!")
            return
        threading.Thread.__init__(self)
        logger.debug("Created thread")
        self.video = video
        self.listeners = finished_listeners  # FIXME: Need one for failed as well?
        self.download_status = None
        self.download_failure_exception = None
        self.download_progress_listener = download_progress_listener
        self.threading_event = threading_event
        # FIXME: faux filename, as the application is currently not able to get final filename from youtube-dl
        file_name = "%(uploader)s - {date} - %(title)s - _v-id-{id}.%(ext)s".format(
            date=self.video.date_published.strftime(
                "%Y-%m-%d"), id=self.video.video_id)
        self.youtube_folder = read_config('Play', 'yt_file_path', literal_eval=False)
        file_path = os.path.join(self.youtube_folder, file_name)

        # Get a list of user-defined (valid) proxies.
        self.proxies = get_valid_options('Youtube-dl_proxies')

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

    @staticmethod
    def add_userconfig_opts(ydl_opts):
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

                with YoutubeDL(self.proxy_ydl_opts) as ydl:
                    logger.info("Starting download (proxy: {}) for: {}".format(proxy, self.video))
                    self.download_status = DOWNLOAD_RUNNING
                    ydl.download([self.video.url_video])
                    self.download_status = DOWNLOAD_FINISHED
                    return True
            except DownloadError as dl_exc:
                self.set_download_failure_exception(dl_exc)
                logger.warning("Proxy {} download of geo blocked video '{}' failed.".format(proxy, self.video))
                logger.exception(dl_exc)
                self.download_status = DOWNLOAD_FAILED
                pass
            except ValueError as ve_exc:
                # Catching the ValueError usually immediately throws another
                self.set_download_failure_exception(ve_exc)
                logger.warning("Proxy {} download of geo blocked video '{}' failed.".format(proxy, self.video))
                logger.exception(ve_exc)
                self.download_status = DOWNLOAD_FAILED
                pass
            except Exception as e:
                self.set_download_failure_exception(e)
                logger.warning("Proxy {} download of geo blocked video '{}' failed.".format(proxy, self.video))
                logger.exception(e)
                self.download_status = DOWNLOAD_FAILED
                pass

        return False

    def guesstimate_filepath_by_id(self):
        for name in os.listdir(self.youtube_folder):
            if self.video.video_id in name and name.split('.')[-1] in VIDEO_FORMATS:
                return os.path.join(self.youtube_folder, name)

    def guesstimate_incomplete_filenames_by_id(self, delete_tempfile=False):
        candidates = []
        for name in os.listdir(self.youtube_folder):
            if self.video.video_id in name and name.split('.')[-1] in VIDEO_FORMATS:
                if delete_tempfile and name.split('.')[-2] == 'temp':
                    logger.info("Deleting 0-byte temp file '{}' from earlier failed ffmpeg merge".format(name))
                    os.remove(os.path.join(self.youtube_folder, name))
                    continue
                candidates.append(name)
        return candidates

    def determine_filepath(self):
        # FIXME: Replace with info grabbed from youtube_dl (hook?)
        return self.guesstimate_filepath_by_id()

    def determine_incomplete_filenames(self, delete_tempfile=False):
        # FIXME: Replace with info grabbed from youtube_dl (hook?)
        names = self.guesstimate_incomplete_filenames_by_id(delete_tempfile=delete_tempfile)
        if len(names) > 1:
            return names
        else:
            logger.error("Unable to determine incomplete filenames, need 2 or more for a merge (got: {})".format(names))
            return None

    @staticmethod
    def delete_filepaths(filepaths):
        for filepath in filepaths:
            logger.info("Deleting format from earlier failed ffmpeg merge: '{}'".format(filepath))
            os.remove(filepath)

    def embed_metadata(self):
        """
        Embeds metadata tags (and optionally remaps them) to media files
        :return:
        """
        logger.info("Embedding metadata with default tags")
        # Keys are media metadata tag names (https://wiki.multimedia.cx/index.php?title=FFmpeg_Metadata)
        # FIXME: Add other presets like music
        # Video as TV-series preset
        info = {'not_a_tag': ['not_a_tag', 'filepath', 'ext'],
                'filepath': self.video.vid_path,
                'ext':      self.video.vid_path.split('.')[-1],
                'title':    self.video.title,
                'show':     self.video.channel_title,
                'date':     self.video.date_published.isoformat(),
                'url':      self.video.url_video,
                'network': 'YouTube',
                ('description', 'comment', 'synopsis'): self.video.description}
        logger.debug(info)
        SaneFFmpegMetadataPP(SaneFFmpegPostProcessor()).run(info)

    def set_download_failure_exception(self, e):
        """
        Updates a variable that keeps a record of the last download failure exception.
        :param e: An Exception.
        :return:
        """
        self.download_failure_exception = e

    def run(self):
        logger.debug("Started download thread")
        self.threading_event.wait()
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                logger.info("Starting download for: {}".format(self.video))
                self.download_status = DOWNLOAD_RUNNING
                ydl.download([self.video.url_video])
                self.download_status = DOWNLOAD_FINISHED
        except DownloadError as dl_exc:
            self.set_download_failure_exception(dl_exc)
            # If the DownloadError is a match for any of the VIDEO_IS_GEOBLOCKED_ERRORS, attempt download with proxy.
            if any(x in str(dl_exc) for x in VIDEO_IS_GEOBLOCKED_ERRORS):
                logger.info("Video is geo blocked, retrying with proxy: {}".format(self.video))
                if self.download_with_proxy() is not True:
                    self.download_status = DOWNLOAD_FAILED
                    logger.error("All proxies have failed to download geo blocked video '{}'!".format(self.video.title))
                    logger.exception(dl_exc)
                else:
                    self.download_status = DOWNLOAD_FINISHED

            if str(dl_exc) in AUDIO_MERGE_FAILS:
                logger.warning("Handling incompatible container audio and video stream muxing",
                               exc_info=dl_exc)
                incomplete_filenames = self.determine_incomplete_filenames(delete_tempfile=True)
                if incomplete_filenames is not None:
                    logger.debug(incomplete_filenames)
                    # Strip the .f** format from the string to reproduce intended output filename
                    output_filename = '{}.{}'.format(incomplete_filenames[0].split('.')[0],
                                                     read_config('Youtube-dl_opts', 'merge_output_format',
                                                                 literal_eval=False))
                    output_filepath = os.path.join(self.youtube_folder, output_filename)
                    incomplete_filepaths = []
                    for filename in incomplete_filenames:
                        incomplete_filepaths.append(os.path.join(self.youtube_folder, filename))

                    info = {'filepath': output_filepath,
                            '__files_to_merge': incomplete_filepaths,
                            'audio_codec': 'libvo_aacenc',
                            'video_codec': 'h264',
                            'no_remux': 'True'}

                    # Merge formats
                    try:
                        SaneFFmpegMergerPP(SaneFFmpegPostProcessor()).run(info)
                        self.download_status = DOWNLOAD_FINISHED
                    except SaneFFmpegPostProcessorError as merge_exc:
                        self.set_download_failure_exception(merge_exc)
                        logger.exception("Failed to merge formats", exc_info=merge_exc)
                        self.download_status = DOWNLOAD_FAILED

                    # Cleanup remnant formats
                    self.delete_filepaths(incomplete_filepaths)

                else:
                    self.download_status = DOWNLOAD_FAILED
                    logger.error("Can't handle incompatible container "
                                 "audio and video stream muxing, insufficent files. | {}".format(incomplete_filenames))
                if str(dl_exc) in IO_ERROR:
                    self.download_status = DOWNLOAD_FAILED
                    logger.exception("Failing download due to DownloadError exception (I/O ERROR)!", exc_info=dl_exc)
                if str(dl_exc) in WRITE_DENIED_ERROR:
                    self.download_status = DOWNLOAD_FAILED
                    logger.exception("Failing download due to DownloadError exception (PermissionError)!",
                                     exc_info=dl_exc)
                if str(dl_exc) in SSL_HANDSHAKE_FAILS:
                    self.download_status = DOWNLOAD_FAILED
                    logger.exception("Failing download due to DownloadError exception (SSL handshake failure)!",
                                     exc_info=dl_exc)
            if self.download_status == DOWNLOAD_RUNNING:
                logger.critical("Setting FAILED status for video with "
                                "lingering DOWNLOADING status : {}".format(self.video))
                logger.exception(dl_exc)
                self.download_status = DOWNLOAD_FAILED

        except PermissionError as pe_exc:
            self.set_download_failure_exception(pe_exc)
            self.download_status = DOWNLOAD_FAILED
            logger.exception("Failing download due to PermissionError exception!", exc_info=pe_exc)

        except Exception as e:
            self.set_download_failure_exception(e)
            self.download_status = DOWNLOAD_FAILED
            logger.exception(e)
            pass

        if self.download_status == DOWNLOAD_FINISHED:
            logger.info("Finished downloading: {}".format(self.video))
            # self.video.vid_path = os.path.join(self.youtube_folder, self.determine_filename())
            self.video.vid_path = self.determine_filepath()

            # self.video.vid_path = os.path.join(self.youtube_folder, self.determine_filename())
            self.video.vid_path = self.determine_filepath()

            self.video.date_downloaded = datetime.datetime.utcnow()

            # Embed metadata (optional)
            if read_config('Postprocessing', 'embed_metadata', literal_eval=True):
                self.embed_metadata()
            else:
                logger.debug("Skipping disabled metadata embedding operation")

            self.download_progress_listener.finishedDownload.emit()
            if self.listeners:
                for listener in self.listeners:
                    listener.emit(self.video)
        elif self.download_status == DOWNLOAD_FAILED:
            logger.error("FAILED downloading: {}".format(self.video))
            self.download_progress_listener.failedDownload.emit(self.download_failure_exception)

    def my_hook(self, event):
        self.download_progress_listener.updateProgress.emit(event)
        self.threading_event.wait()
