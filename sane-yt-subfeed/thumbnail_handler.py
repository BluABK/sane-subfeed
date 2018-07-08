import os
import shutil
import threading
import time

from tqdm import tqdm

from .config_handler import read_config
from .pickle_handler import PICKLE_PATH, load_pickle
import certifi
import urllib3

OS_PATH = os.path.dirname(__file__)
THUMBNAILS_PATH = os.path.join(OS_PATH, 'resources', 'thumbnails')

class DownloadThumbnail(threading.Thread):

    def __init__(self, video, thread_list):
        threading.Thread.__init__(self)
        self.video = video
        self.thread_list = thread_list

    def run(self):
        vid_path = os.path.join(OS_PATH, 'resources', 'thumbnails', '{}.jpg'.format(self.video.video_id))
        if not os.path.exists(vid_path):
            thumbnail_dict = get_best_thumbnail(self.video)
            # print(thumbnail_dict)
            download_file(thumbnail_dict['url'], vid_path)
        self.thread_list.remove(self)


def get_thumbnail_path(vid):
    return os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(vid.video_id))


def download_thumbnails_seq(vid_list):
    path_list = []
    for video in vid_list:
        vid_path = os.path.join(OS_PATH, 'resources', 'thumbnails', '{}.jpg'.format(video.video_id))
        if not os.path.exists(vid_path):
            thumbnail_dict = get_best_thumbnail(video.thumbnails)
            # print(thumbnail_dict)
            download_file(thumbnail_dict['url'], vid_path)
        path_list.append(vid_path)
    return path_list


def download_thumbnails_threaded(vid_list):
    thread_list = []
    thread_limit = int(read_config('Threading', 'img_threads'))
    print("\nStarting thumbnail download threads")
    for video in tqdm(vid_list):
        t = DownloadThumbnail(video, thread_list)
        thread_list.append(t)
        t.start()
        # print(len(thread_list))
        while len(thread_list) >= thread_limit:
            print(len(thread_list))
            time.sleep(0.0001)
            # thread = thread_list.pop(0)
            # thread.join()


    print("\nWaiting for download threads to finish")
    for t in tqdm(thread_list):
        t.join()


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

# if __name__ == "__main__":
#     jesse_vids = load_pickle(os.path.join(PICKLE_PATH, 'jesse_vid_dump.pkl'))
    # test_run = 0
    # for vid in jesse_vids:
    #     thumbnail_dict = get_best_thumbnail(vid)
    #     path = os.path.join(OS_PATH, 'resources', 'thumbnails', '{}.jpg'.format(vid.video_id))
    #     # download_file(thumbnail_dict['url'], path)
    #     if test_run == 2:
    #         break
    #     test_run += 1
    # print(download_thumbnails_threaded(jesse_vids))
