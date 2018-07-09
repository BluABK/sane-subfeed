import os
import shutil
import threading
import time
from collections import defaultdict

from tqdm import tqdm

import certifi
import urllib3

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.pickle_handler import load_pickle, PICKLE_PATH
from sane_yt_subfeed.database.video import Video

OS_PATH = os.path.dirname(__file__)
THUMBNAILS_PATH = os.path.join(OS_PATH, '..', 'resources', 'thumbnails')


class DownloadThumbnail(threading.Thread):

    def __init__(self, thread_list, video_id, force_dl_best, thumbnail_dict):
        threading.Thread.__init__(self)
        self.thread_list = thread_list
        self.video_id = video_id
        self.force_dl_best = force_dl_best
        self.thumbnail_dict = thumbnail_dict

    def run(self):
        vid_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(self.video_id))
        if not os.path.exists(vid_path):
            if self.force_dl_best:
                force_download_best(self.video_id, vid_path)
            else:
                download_file(self.thumbnail_dict['url'], vid_path)


def get_thumbnail_path(vid):
    return os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(vid.video_id))


def download_thumbnails_threaded(vid_list):
    thread_list = []
    thread_limit = int(read_config('Threading', 'img_threads'))
    print("\nStarting thumbnail download threads")
    force_dl_best = read_config('Thumbnails', 'force_download_best')
    for vid in vid_list:
        vid_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(vid.video_id))
        vid.thumbnail_path = vid_path
        thumbnail_dict = get_best_thumbnail(vid)
        t = DownloadThumbnail(thread_list, vid.video_id, force_dl_best, thumbnail_dict)
        thread_list.append(t)
        t.start()
        while len(thread_list) >= thread_limit:
            time.sleep(0.0001)

    print("\nWaiting for download threads to finish")
    for t in tqdm(thread_list):
        t.join()

    print("\nAll threads done")
    db_session.commit()

def set_thumbnail(video):
    vid_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(video.video_id))
    if not os.path.exists(vid_path):
        force_dl_best = read_config('Thumbnails', 'force_download_best')
        if force_dl_best:
            force_download_best(video, vid_path)
        else:
            thumbnail_dict = get_best_thumbnail(video)
            download_file(thumbnail_dict['url'], vid_path)
    video.thumbnail_path = vid_path


def thumbnails_dl_and_paths(vid_list):
    download_thumbnails_threaded(vid_list)
    path_list = []
    for vid in vid_list:
        path_list.append(get_thumbnail_path(vid))
    return path_list


def jesse_pickle():
    return load_pickle(os.path.join(PICKLE_PATH, 'jesse_vid_dump.pkl'))


def download_file(url, path):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    with http.request('GET', url, preload_content=False) as r, open(path, 'wb') as out_file:
        shutil.copyfileobj(r, out_file)


def get_best_thumbnail(vid):
    for i in range(5):
        quality = read_config('Thumbnails', '{}'.format(i))
        if quality in vid.thumbnails:
            return_dict = vid.thumbnails[quality]
            return_dict.update({'quality': quality})
            return return_dict
    return {}


def force_download_best(vid_id, vid_path):
    url = 'https://i.ytimg.com/vi/{vid_id}/'.format_map(defaultdict(vid_id=video_id))
    print(url)
    for i in range(5):
        quality = read_config('Thumbnails', '{}'.format(i))
        if quality == 'maxres':
            try:
                temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='maxresdefault'))
                print(temp_url)
                print(url)
                download_file(temp_url, vid_path)
            except Exception as e:
                raise e

