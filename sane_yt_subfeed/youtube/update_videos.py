import re
from datetime import timedelta
from googleapiclient.errors import HttpError
from tqdm import tqdm

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.static_controller_vars import LISTENER_SIGNAL_NORMAL_REFRESH, \
    LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.exceptions.sane_aborted_operation import SaneAbortedOperation
from sane_yt_subfeed.generate_keys import GenerateKeys
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.pickle_handler import load_batch_build_key, dump_batch_build_key
from sane_yt_subfeed.youtube.uploads_thread import GetUploadsThread
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions, get_videos_result

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)

# Thread exception lists
refresh_ul_thread_exc_http = []
refresh_ul_thread_exc_other = []

abort = False


def refresh_uploads(progress_bar_listener=None, add_to_max=0,
                    refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
    """
    Refresh the subscription feed with new entries, if any.

    Throws SaneAbortedOperation exception if any critical exceptions occurs.
    :param progress_bar_listener:
    :param add_to_max:
    :param refresh_type:
    :return:
    """
    global abort
    thread_increment = 0
    thread_list = []
    videos = []
    cached_subs = read_config('Debug', 'cached_subs')
    subscriptions = get_subscriptions(cached_subs)
    youtube_keys = load_keys(len(subscriptions))

    search_pages = [1, 1]
    deep_search = False

    if refresh_type == LISTENER_SIGNAL_DEEP_REFRESH:
        quota_k = read_config('Requests', 'deep_search_quota_k')
        search_pages = deep_search_calc(quota_k, subscriptions)
        deep_search = True

    if progress_bar_listener:
        progress_bar_listener.setMaximum.emit(2 * len(subscriptions) + add_to_max)

    channels_limit = read_config('Debug', 'channels_limit')
    for channel, youtube in tqdm(zip(subscriptions, youtube_keys), desc="Creating video update threads",
                                 disable=read_config('Debug', 'disable_tqdm')):
        thread = GetUploadsThread(thread_increment, youtube, channel.id, channel.playlist_id, videos, search_pages[0],
                                  search_pages[1], deep_search=deep_search)
        thread_list.append(thread)
        thread_increment += 1

        if 0 < channels_limit <= thread_increment:
            break

    if progress_bar_listener:
        progress_bar_listener.setText.emit('Starting video update threads')

    for t in tqdm(thread_list, desc="Starting video update threads", disable=read_config('Debug', 'disable_tqdm')):
        if progress_bar_listener:
            progress_bar_listener.updateProgress.emit()
        t.start()

    if progress_bar_listener:
        progress_bar_listener.setText.emit('Waiting for video update threads')

    exceptions = []
    for t in tqdm(thread_list, desc="Waiting for video update threads", disable=read_config('Debug', 'disable_tqdm')):
        if progress_bar_listener:
            progress_bar_listener.updateProgress.emit()
        try:
            if not abort:
                t.join()
            else:
                # Delete thread due to abort condition being set.
                del t
        # Store exceptions to lists, because raise breaks joining process and return
        except HttpError as exc_gapi_http_error:  # FIXME: Handle HttpError exceptions
            # Don't abort because the job might still be mostly successful.
            logger.error("A Google API HttpError exception occurred in thread {}! -- !!IMPLEMENT HANDLING!!".format(
                t.thread_id), exc_info=exc_gapi_http_error)
            refresh_ul_thread_exc_http.append(exc_gapi_http_error)
            pass
        except OSError as exc_ose:
            # Abort the entire operation since this usually means several (if not all) operations will fail.
            abort = True

            # Handle hitting the file descriptor ceiling.
            if "Too many open files" in str(exc_ose):
                _ = "refresh_uploads() hit fd ceiling with thread #{}! " \
                    "Aborting job and deleting unjoined threads..".format(t.thread_id)
                logger.critical(_, exc_info=exc_ose)
                del t
                exceptions.append(exc_ose)
            else:
                logger.critical("An *UNEXPECTED* OSError exception occurred in thread #{}!".format(t.thread_id),
                                exc_info=exc_ose)
                exceptions.append(exc_ose)
                refresh_ul_thread_exc_other.append(exc_ose)  # FIXME: Is this actually used?
                pass
        except Exception as exc_other:
            # Abort the entire operation since this usually means several (if not all) operations will fail.
            abort = True

            logger.critical("An *UNEXPECTED* exception occurred in thread #{}!".format(t.thread_id), exc_info=exc_other)

            exceptions.append(exc_other)
            refresh_ul_thread_exc_other.append(exc_other)  # FIXME: Is this actually used?
            pass

    if abort:
        abort = False
        raise SaneAbortedOperation("Refresh uploads operation ABORTED due to critical exceptions.",
                                   exceptions=exceptions)
    else:
        return sorted(videos, key=lambda video: video.date_published, reverse=True)


def load_keys(number_of_keys):
    youtube_keys = []
    try:
        youtube_keys = load_batch_build_key()
    except FileNotFoundError:
        logger.info("load_batch_build_key() gave 404 error. Generating new youtube key builds.")
        print("\nGenerating youtube key builds:")
        youtube_keys.extend(generate_keys(number_of_keys))
        dump_batch_build_key(youtube_keys)

    diff = number_of_keys - len(youtube_keys)
    if diff > 0:
        logger.info("Generating diff youtube key builds.")
        print("\nGenerating diff youtube key builds:")
        youtube_keys.extend(generate_keys(diff))
        dump_batch_build_key(youtube_keys)
    return youtube_keys


def generate_keys(key_number):
    keys = []
    threads = []

    logger.info("Starting key generation threads.")
    for _ in tqdm(range(key_number), desc="Starting key generation threads",
                  disable=read_config('Debug', 'disable_tqdm')):
        t = GenerateKeys(keys)
        t.start()
        threads.append(t)

    logger.info("Waiting for key generation threads.")
    for t in tqdm(threads, desc="Waiting for key generation threads", disable=read_config('Debug', 'disable_tqdm')):
        t.join()
    return keys


def yt_duration_to_timedeltat(time_str):
    # regex = re.compile(r'((?P<hours>\d+?)T)?((?P<minutes>\d+?)M)?((?P<seconds>\d+?)S)?')
    # regex = re.compile(r'((?P<days>\d*)P)?((?P<hours>\d*)T)?((?P<minutes>\d*)M)?((?P<seconds>\d*)S)?')
    regex = re.compile(r'((?P<days>\d*)PT)?((?P<hours>\d*)H)?((?P<minutes>\d*)M)?((?P<seconds>\d*)S)?')

    parts = regex.match(time_str)
    if not parts:
        logger.error("YT Duration failed timedelta conversion (parts=None): {}".format(time_str))
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def boolify_string(s):
    """
    Uppercase first letter and eval a 'false'/'true' string to a Python boolean
    :param s: case-insensitive string value that is either 'false' or 'true'
    :return: A Boolean or None (if invalid)
    """
    valid_bools = ['true', 'false']
    if s.lower() not in valid_bools:
        logger.error("Attempted to boolify invalid string: '{}'".format(s))
        return

    return eval(s.lower()[0].upper() + s.lower()[1:])


def get_extra_videos_information(videos):
    """
    Retrieves and sets additional information for videos that is only available through the 'videos' API call
    :param videos: A list of video objects
    :return:
    """
    youtube_keys = load_keys(1)
    video_ids = list(vid.video_id for vid in videos)
    logger.info("Grabbing extra video(s) information from youtube for: {}".format(videos))
    response_videos = []
    chunk_size = 50
    for i in range(0, len(videos), max(chunk_size, 1)):
        response_videos.extend(
            get_videos_result(youtube_keys[0], video_ids[i:i + chunk_size], 30, part="contentDetails"))
    for response in response_videos:
        for video in videos:
            if str(response['id']) == video.video_id:
                # logger.info("video (response): {} - {}".format(video.channel_title, video.title))
                # logger.info(response)
                duration = yt_duration_to_timedeltat(response['contentDetails']['duration'])
                video.duration = duration
                video.has_caption = boolify_string(response['contentDetails']['caption'])
                video.dimension = response['contentDetails']['dimension']
                video.definition = response['contentDetails']['definition']
                video.projection = response['contentDetails']['projection']
                # regionRestriction and its sub-items seems to only exist if explicitly set
                if 'regionRestriction' in response['contentDetails']:
                    if 'allowed' in response['contentDetails']['regionRestriction']:
                        video.region_restriction_allowed = response['contentDetails']['regionRestriction']['allowed']
                    if 'blocked' in response['contentDetails']['regionRestriction']:
                        video.region_restriction_blocked = response['contentDetails']['regionRestriction']['blocked']
    return videos


def deep_search_calc(quota_k, subscriptions):
    subscriptions_len = len(subscriptions)
    quota = quota_k * 1000
    max_search_quota = int(0.9 * quota)

    search_mod = divmod(max_search_quota, subscriptions_len * 100)

    search_pages = search_mod[0]
    list_pages = int((quota - max_search_quota + search_mod[1]) / (subscriptions_len * 3))

    return [list_pages, search_pages]
