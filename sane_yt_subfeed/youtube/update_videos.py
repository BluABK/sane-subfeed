import time

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners import ProgressBar
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.generate_keys import GenerateKeys
from sane_yt_subfeed.pickle_handler import load_batch_build_key, dump_batch_build_key
from sane_yt_subfeed.youtube.uploads_thread import GetUploadsThread
from tqdm import tqdm  # fancy progress bar

from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO


def refresh_uploads(progress_bar_listener: ProgressBar=None):
    thread_increment = 0
    thread_list = []
    videos = []
    cached_subs = read_config('Debug', 'cached_subs')
    subscriptions = get_subscriptions(cached_subs)
    youtube_keys = load_keys(subscriptions)
    if progress_bar_listener:
        progress_bar_listener.resetBar.emit()
        progress_bar_listener.setMaximum.emit(2*len(subscriptions))

    channels_limit = read_config('Debug', 'channels_limit')
    for channel, youtube in tqdm(zip(subscriptions, youtube_keys), desc="Creating video update threads",
                                 disable=read_config('Debug', 'disable_tqdm')):
        thread = GetUploadsThread(thread_increment, youtube, channel.id, channel.playlist_id, videos, 1)
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


def load_keys(subs):
    youtube_keys = []
    try:
        youtube_keys = load_batch_build_key()
    except FileNotFoundError:
        print("\nGenerating youtube key builds:")
        youtube_keys.extend(generate_keys(len(subs)))
        dump_batch_build_key(youtube_keys)

    diff = len(subs) - len(youtube_keys)
    if diff > 0:
        print("\nGenerating diff youtube key builds:")
        youtube_keys.extend(generate_keys(diff))
        dump_batch_build_key(youtube_keys)
    return youtube_keys


def generate_keys(key_number):
    keys = []
    threads = []

    for _ in tqdm(range(key_number), desc="Starting key generation threads",
                  disable=read_config('Debug', 'disable_tqdm')):
        t = GenerateKeys(keys)
        t.start()
        threads.append(t)

    for t in tqdm(threads, desc="Waiting for key generation threads", disable=read_config('Debug', 'disable_tqdm')):
        t.join()
    return keys
