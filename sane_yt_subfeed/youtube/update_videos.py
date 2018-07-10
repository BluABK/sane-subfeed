import time

from sane_yt_subfeed.config_handler import read_config
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


def refresh_uploads():

    thread_increment = 0
    thread_list = []
    videos = []
    cached_subs = read_config('Debug', 'cached_subs')
    subscriptions = get_subscriptions(cached_subs)
    youtube_keys = load_keys(subscriptions)

    print("Creating YouTube service object from API_KEY for %s channels:" % len(subscriptions))
    channels_limit = read_config('Debug', 'channels_limit')
    for channel, youtube in tqdm(zip(subscriptions, youtube_keys)):
        thread = GetUploadsThread(thread_increment, youtube, channel.id, videos, 1)
        thread_list.append(thread)
        thread_increment += 1
        if 0 < channels_limit <= thread_increment:
            break
        # if thread_increment >= thread_limit:
        #     break
    print("\nStarting threads:")
    for t in tqdm(thread_list):
        t.start()

    print("\nCollecting data from %s threads:" % len(thread_list))
    for t in tqdm(thread_list):
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

    print("\nStarting key generation threads:")
    for _ in tqdm(range(key_number)):
        t = GenerateKeys(keys)
        t.start()
        threads.append(t)

    print("\nClosing key generation threads:")
    for t in tqdm(threads):
        t.join()
    return keys
