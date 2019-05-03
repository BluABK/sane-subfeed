import re
import time
from datetime import timedelta
from googleapiclient.errors import HttpError

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.controller.static_controller_vars import LISTENER_SIGNAL_NORMAL_REFRESH, \
    LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.exceptions.sane_aborted_operation import SaneAbortedOperation
from sane_yt_subfeed.youtube.generate_keys import GenerateKeys
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.handlers.pickle_handler import load_youtube_resource_keys, save_youtube_resource_keys
from sane_yt_subfeed.youtube.uploads_thread import GetUploadsThread
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions, get_videos_result

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)


def reinstantiate_thread(t):
    """
    Creates a new thread from an old one, and then deletes the old one and returns the new one.

    This is necessary because a thread can only be started once.
    :param t: GetUploadsThread object
    :return: GetUploadsThread
    """
    # Gather necessary data from the old thread instance.
    thread_id = t.thread_id
    youtube = t.youtube
    channel_id = t.channel_id
    channel_playlist_id = t.playlist_id
    videos = t.videos
    list_pages = t.list_pages
    search_pages = t.search_pages
    deep_search = t.deep_search

    # Create a new thread instance based on the old thread instance's data.
    new_t = GetUploadsThread(thread_id, youtube, channel_id, channel_playlist_id, videos, list_pages,
                             search_pages, deep_search=deep_search)

    # Delete the old failed thread instance.
    del t

    # Return the new thread instance.
    return new_t


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
    for channel, youtube in zip(subscriptions, youtube_keys):
        thread = GetUploadsThread(thread_increment, youtube, channel.id, channel.playlist_id, videos, search_pages[0],
                                  search_pages[1], deep_search=deep_search)
        thread_list.append(thread)
        thread_increment += 1

        if 0 < channels_limit <= thread_increment:
            break

    if progress_bar_listener:
        progress_bar_listener.setText.emit('Starting video update threads')

    for t in thread_list:
        if progress_bar_listener:
            progress_bar_listener.updateProgress.emit()
        t.start()

    if progress_bar_listener:
        progress_bar_listener.setText.emit('Waiting for video update threads')

    exceptions = []
    abort_all_threads = False
    for t in thread_list:
        if abort_all_threads:
            # Delete current thread (also implies all following threads)
            del t
        if progress_bar_listener:
            progress_bar_listener.updateProgress.emit()

        attempt = 1
        joined_thread = False
        abort_current_thread = False
        max_attempts = read_config('Threading', 'retry_attempts')
        while not abort_all_threads and not joined_thread:
            if attempt <= max_attempts and not abort_current_thread:
                failed_attempt = False
                try:
                    t.join()

                except HttpError as exc_gapi_http_error:  # FIXME: Handle more HttpError exceptions
                    if "HttpError 500 when requesting" in str(exc_gapi_http_error):
                        if 'returned "Backend Error"' in str(exc_gapi_http_error):
                            log_msg = "A Google API HttpError 500 " \
                                      "(Backend Error) occurred in thread #{}" \
                                      "(channel: {}, playlist: {})".format(t.thread_id, t.channel_id, t.playlist_id)

                            if attempt == max_attempts:
                                # The final attempt has failed
                                logger.error("{}, attempt {}/{} failed! Giving up on this thread...".format(
                                              log_msg, attempt, max_attempts),
                                             exc_info=exc_gapi_http_error)
                            else:
                                # Don't abort because the job might still be mostly successful.
                                logger.warning("{}, retrying... [{}/{}]".format(
                                                log_msg, attempt, max_attempts),
                                               exc_info=exc_gapi_http_error)

                            # Store exceptions to lists, because raise breaks joining process and return
                            exceptions.append(exc_gapi_http_error)

                            # Re-run the failed thread job
                            time.sleep(read_config('Threading', 'retry_delay'))
                            t = reinstantiate_thread(t)
                            t.start()
                            pass
                    else:
                        log_msg = "(An unexpected Google API HttpError occurred in thread #{}" \
                                  "(channel: {}, playlist: {})".format(t.thread_id, t.channel_id, t.playlist_id)

                        if attempt == max_attempts:
                            # The final attempt has failed
                            logger.error("{}, attempt {}/{} failed! Giving up on this thread...".format(
                                log_msg, attempt, max_attempts),
                                exc_info=exc_gapi_http_error)
                        else:
                            # Don't abort because the job might still be mostly successful.
                            logger.error("{}, "
                                         "retrying... [{}/{}]: {}".format(
                                          log_msg, attempt, max_attempts, str(exc_gapi_http_error)),
                                         exc_info=exc_gapi_http_error)

                        # Store exceptions to lists, because raise breaks joining process and return
                        exceptions.append(exc_gapi_http_error)

                        # Re-run the failed thread job
                        time.sleep(read_config('Threading', 'retry_delay'))
                        t = reinstantiate_thread(t)
                        t.start()

                    failed_attempt = True
                    pass
                except OSError as exc_ose:
                    # Handle hitting the file descriptor ceiling.
                    if "Too many open files" in str(exc_ose):
                        logger.critical("refresh_uploads() hit fd ceiling with thread #{}. Aborting all!".format(
                            t.thread_id), exc_info=exc_ose)

                    else:
                        logger.critical("An unexpected OSError exception occurred in thread #{}. Aborting all!".format(
                            t.thread_id), exc_info=exc_ose)

                    # Store exceptions to lists, because raise breaks joining process and return
                    exceptions.append(exc_ose)

                    # Delete current thread
                    del t

                    # Abort the entire operation since this usually means several (if not all) operations will fail.
                    abort_all_threads = True
                    pass
                except Exception as exc_other:
                    logger.critical("An unexpected exception occurred in thread #{}. Aborting all!".format(t.thread_id),
                                    exc_info=exc_other)

                    # Store exceptions to lists, because raise breaks joining process and return
                    exceptions.append(exc_other)

                    # Delete current thread
                    del t

                    # Abort the entire operation since this usually means several (if not all) operations will fail.
                    abort_all_threads = True

                    pass
                finally:
                    attempt += 1

                if not failed_attempt:
                    # If nothing set failed_attempt variable, assume thread joined successfully.
                    joined_thread = True
            else:
                # Delete current thread due to abort condition being set.
                del t

    if abort_all_threads:
        raise SaneAbortedOperation("Refresh uploads operation ABORTED due to critical exceptions.",
                                   exceptions=exceptions)
    else:
        return sorted(videos, key=lambda video: video.date_published, reverse=True)


def load_keys(number_of_keys):
    youtube_keys = []
    try:
        youtube_keys = load_youtube_resource_keys()
    except FileNotFoundError as file404_exc:
        logger.info("load_youtube_resource_keys() gave 404 error. Generating new youtube key builds.",
                    exc_info=file404_exc)
        youtube_keys.extend(generate_keys(number_of_keys))
        save_youtube_resource_keys(youtube_keys)
    except ModuleNotFoundError as mod404_exc:
        logger.info("load_youtube_resource_keys() gave ModuleNotFoundError error. Generating new youtube key builds.",
                    exc_info=mod404_exc)
        youtube_keys.extend(generate_keys(number_of_keys))
        save_youtube_resource_keys(youtube_keys)
    except Exception as exc:
        logger.info("load_youtube_resource_keys() gave Unexpected exception error. Generating new youtube key builds.",
                    exc_info=exc)
        youtube_keys.extend(generate_keys(number_of_keys))
        save_youtube_resource_keys(youtube_keys)

    diff = number_of_keys - len(youtube_keys)
    if diff > 0:
        logger.info("Generating diff youtube key builds.")
        youtube_keys.extend(generate_keys(diff))
        save_youtube_resource_keys(youtube_keys)
    return youtube_keys


def generate_keys(key_number):
    keys = []
    threads = []

    logger.info("Starting key generation threads.")
    for _ in range(key_number):
        t = GenerateKeys(keys)
        t.start()
        threads.append(t)

    logger.info("Waiting for key generation threads.")
    for t in threads:
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
