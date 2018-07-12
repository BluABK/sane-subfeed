import os
import shutil
import threading
import time
from collections import defaultdict
from PIL import Image  # Image cropping (black barred thumbs, issue #11)
from PIL import ImageChops

from tqdm import tqdm

import certifi
import urllib3

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.pickle_handler import load_pickle, PICKLE_PATH
from sane_yt_subfeed.database.video import Video

OS_PATH = os.path.dirname(__file__)
THUMBNAILS_PATH = os.path.join(OS_PATH, '..', 'resources', 'thumbnails')


class DownloadThumbnail(threading.Thread):

    def __init__(self, thread_list, video, force_dl_best, thumbnail_dict):
        threading.Thread.__init__(self)
        self.thread_list = thread_list
        self.video = video
        self.force_dl_best = force_dl_best
        self.thumbnail_dict = thumbnail_dict

    def run(self):
        vid_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(self.video.video_id))
        self.video.thumbnail_path = vid_path
        if not os.path.exists(vid_path):
            if self.force_dl_best:
                force_download_best(self.video)
            else:
                quality = get_best_thumbnail(self.video)
                download_file(self.thumbnail_dict['url'], vid_path, crop=True, quality=quality)


def get_thumbnail_path(vid):
    return os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(vid.video_id))


def download_thumbnails_threaded(vid_list):
    thread_list = []
    thread_limit = int(read_config('Threading', 'img_threads'))
    force_dl_best = read_config('Thumbnails', 'force_download_best')
    for vid in vid_list:
        thumbnail_dict = get_best_thumbnail(vid)
        t = DownloadThumbnail(thread_list, vid, force_dl_best, thumbnail_dict)
        thread_list.append(t)
        t.start()
        while len(thread_list) >= thread_limit:
            time.sleep(0.0001)

    for t in tqdm(thread_list, desc="Waiting on thumbnail threads", disable=read_config('Debug', 'disable_tqdm')):
        t.join()

    # UpdateVideosThread(vid_list).start()
    return vid_list
    # db_session.commit()


def set_thumbnail(video):
    vid_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(video.video_id))
    if not os.path.exists(vid_path):
        force_dl_best = read_config('Thumbnails', 'force_download_best')
        if force_dl_best:
            force_download_best(video)
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


def download_file(url, path, crop=False, quality=None):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    with http.request('GET', url, preload_content=False) as r, open(path, 'wb') as out_file:
        shutil.copyfileobj(r, out_file)
    # FIXME: Move crop to a proper place -- HACK: crop images as they get downloaded
    if quality_404_check(path):
        return False
    if crop:
        crop_blackbars(path, quality)
    return True


def get_best_thumbnail(vid):
    for i in range(5):
        quality = read_config('Thumbnails', '{}'.format(i))
        if quality in vid.thumbnails:
            return_dict = vid.thumbnails[quality]
            return_dict.update({'quality': quality})
            return return_dict
    return {}


def force_download_best(video):
    vid_path = video.thumbnail_path
    url = 'https://i.ytimg.com/vi/{vid_id}/'.format_map(defaultdict(vid_id=video.video_id))
    for i in range(5):
        quality = read_config('Thumbnails', '{}'.format(i))
        if quality == 'maxres':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='maxresdefault'))
            if download_file(temp_url, vid_path, crop=False, quality=quality):
                # Got 404 image, try lower quality
                break
        if quality == 'standard':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='sddefault'))
            if download_file(temp_url, vid_path, crop=False, quality=quality):
                # Got 404 image, try lower quality
                break
        if quality == 'high':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='hqdefault'))
            if download_file(temp_url, vid_path, crop=True, quality=quality):
                # Got 404 image, try lower quality
                break
        if quality == 'medium':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='mqdefault'))
            if download_file(temp_url, vid_path, crop=True, quality=quality):
                # Got 404 image, try lower quality
                break
        if quality == 'default':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='default'))
            if download_file(temp_url, vid_path, crop=True, quality=quality):
                # Got 404 image, try lower quality... Oh wait there is none! uh-oh....
                print("ERROR: force_download_best() tried to go lower than 'default' quality!")
                break


def crop_blackbars(image_filename, quality):
    """
    Crop certain thumbnails that come shipped with black bars above and under
    Qualities affected by this affliction, and actions taken:
        high: 480x360 with bars --> crop to 480x270

    coords: A tuple of x/y coordinates (x1, y1, x2, y2) or (left, top, right, bottom)
    :param image_filename:
    :param image_path:
    :param quality:
    :return:
    """

    img = Image.open(image_filename)
    coords = None
    if quality == 'high':
        coords = (0, 45, 480, (360-45))
    cropped_img = img.crop(coords)
    cropped_img.save(os.path.join(THUMBNAILS_PATH, image_filename))


def quality_404_check(img):
    """
    Checks if the given image matches the YouTube 404: Thumbnail not found image
    :param img:
    :return: True if given image equals YouTube's 404 image
    """
    img_404 = Image.open(os.path.join(OS_PATH, '..', 'resources', 'quality404.jpg'))
    img_cmp = Image.open(img)
    return ImageChops.difference(img_cmp, img_404).getbbox() is None
