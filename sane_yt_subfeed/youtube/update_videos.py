from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.generate_keys import GenerateKeys
from sane_yt_subfeed.pickle_handler import load_batch_build_key, dump_batch_build_key
from sane_yt_subfeed.youtube.uploads_thread import GetUploadsThread
from sane_yt_subfeed.controller.static_controller_vars import LISTENER_SIGNAL_NORMAL_REFRESH, LISTENER_SIGNAL_DEEP_REFRESH
from tqdm import tqdm

from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions
from sane_yt_subfeed.log_handler import create_logger

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO

logger = create_logger("update_videos")


def refresh_uploads(progress_bar_listener=None, add_to_max=0,
                    refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
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
        # if thread_increment >= thread_limit:
        #     break

    if progress_bar_listener:
        progress_bar_listener.setText.emit('Starting video update threads')

    for t in tqdm(thread_list, desc="Starting video update threads", disable=read_config('Debug', 'disable_tqdm')):
        if progress_bar_listener:
            progress_bar_listener.updateProgress.emit()
        t.start()

    if progress_bar_listener:
        progress_bar_listener.setText.emit('Waiting for video update threads')

    for t in tqdm(thread_list, desc="Waiting for video update threads", disable=read_config('Debug', 'disable_tqdm')):
        if progress_bar_listener:
            progress_bar_listener.updateProgress.emit()
        t.join()

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


def deep_search_calc(quota_k, subscriptions):
    subscriptions_len = len(subscriptions)
    quota = quota_k * 1000
    max_search_quota = int(0.9 * quota)

    search_mod = divmod(max_search_quota, subscriptions_len * 100)

    search_pages = search_mod[0]
    list_pages = int((quota - max_search_quota + search_mod[1]) / (subscriptions_len * 3))

    return [list_pages, search_pages]
