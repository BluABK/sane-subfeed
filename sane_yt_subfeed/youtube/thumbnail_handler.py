import math
from collections import defaultdict

import certifi
import os
import shutil
import threading
import urllib3
from PIL import Image  # Image cropping (black barred thumbs, issue #11)
from PIL import ImageChops

from sane_yt_subfeed.absolute_paths import THUMBNAILS_PATH, THUMBNAIL_404_PATH, THUMBNAIL_NA_PATH, \
    THUMBNAILS_RESIZED_PATH
from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.handlers.log_handler import create_logger


# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)


class DownloadThumbnail(threading.Thread):

    def __init__(self, videos, force_dl_best=True, progress_listener=None):
        threading.Thread.__init__(self)
        self.logger = create_logger(__name__ + ".DownloadThumbnail")
        self.videos = videos
        self.force_dl_best = force_dl_best
        self.progress_listener = progress_listener

    def run(self):
        for video in self.videos:
            vid_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(video.video_id))
            video.thumbnail_path = vid_path
            if not os.path.exists(vid_path):
                if self.force_dl_best:
                    force_download_best(video)
                    if not os.path.exists(vid_path):
                        self.logger.warning(
                            "force_download_best failed to download thumbnail for: {}".format(video.__dict__))
                else:
                    thumbnail_dict = get_best_thumbnail(video)
                    quality = get_best_thumbnail(video)
                    crop = False
                    if 'standard' in quality['quality'] or 'high' in quality['quality'] or 'default' in quality[
                       'quality']:
                        crop = True
                    download_thumb_file(thumbnail_dict['url'], vid_path, crop=crop, quality=quality['quality'])
                    if not os.path.exists(vid_path):
                        self.logger.warning(
                            "download_thumb_file failed to download thumbnail for: {}".format(video.__dict__))
            if self.progress_listener:
                self.progress_listener.updateProgress.emit()


def get_thumbnail_path(vid):
    return os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(vid.video_id))


def download_thumbnails_threaded(input_vid_list, progress_listener=None):
    download_thumbnails_threaded_logger = create_logger(__name__ + ".download_thumbnails_threaded")

    thread_list = []
    thread_limit = int(read_config('Threading', 'img_threads'))
    force_dl_best = read_config('Thumbnails', 'force_download_best')

    if progress_listener:
        progress_listener.setText.emit('Downloading thumbnails')

    vid_list = []
    chunk_size = math.ceil(len(input_vid_list) / thread_limit)
    for i in range(0, len(input_vid_list), max(chunk_size, 1)):
        vid_list.append(input_vid_list[i:i + chunk_size])
    counter = 0

    download_thumbnails_threaded_logger.info(
        "Starting thumbnail download threads for {} videos in {} threads".format(len(input_vid_list), len(vid_list)))
    for vid_list_chunk in vid_list:
        t = DownloadThumbnail(vid_list_chunk, force_dl_best=force_dl_best, progress_listener=progress_listener)
        thread_list.append(t)
        t.start()
        counter += 1
        if progress_listener:
            progress_listener.updateProgress.emit()
    for t in thread_list:
        t.join()


def set_thumbnail(video):
    vid_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(video.video_id))
    if not os.path.exists(vid_path):
        force_dl_best = read_config('Thumbnails', 'force_download_best')
        if force_dl_best:
            force_download_best(video)
        else:
            thumbnail_dict = get_best_thumbnail(video)
            crop = False
            if 'standard' in thumbnail_dict['quality'] or 'high' in thumbnail_dict['quality'] or 'default' in \
                    thumbnail_dict['quality']:
                crop = True
            download_thumb_file(thumbnail_dict['url'], vid_path, quality=thumbnail_dict['quality'], crop=crop)
    video.thumbnail_path = vid_path


def thumbnails_dl_and_paths(vid_list):
    download_thumbnails_threaded(vid_list)
    path_list = []
    for vid in vid_list:
        path_list.append(get_thumbnail_path(vid))
    return path_list


def download_thumb_file(url, path, crop=False, quality=None, check_404=False):
    """
    Downloads a thumbnail image file
    :param url:         Thumbnail image direct download url
    :param path:        Thumbnail image file save/disk location
    :param crop:        Whether or not to crop black barred thumbnails to their intended size
    :param quality:     Thumbnail quality (maxres, standard, high, medium, default)
    :param check_404:   Whether or not to check if downloaded image file is the YouTube 404 image
    :return:
    """
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    with http.request('GET', url, preload_content=False) as r, open(path, 'wb') as out_file:
        shutil.copyfileobj(r, out_file)
    if check_404:
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
            if download_thumb_file(temp_url, vid_path, crop=False, quality=quality, check_404=True):
                # Got 404 image, try lower quality
                break
        if quality == 'standard':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='sddefault'))
            if download_thumb_file(temp_url, vid_path, crop=True, quality=quality, check_404=True):
                # Got 404 image, try lower quality
                break
        if quality == 'high':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='hqdefault'))
            if download_thumb_file(temp_url, vid_path, crop=True, quality=quality, check_404=True):
                # Got 404 image, try lower quality
                break
        if quality == 'medium':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='mqdefault'))
            if download_thumb_file(temp_url, vid_path, crop=False, quality=quality, check_404=True):
                # Got 404 image, try lower quality
                break
        if quality == 'default':
            temp_url = url + '{url_quality}.jpg'.format_map(defaultdict(url_quality='default'))
            if download_thumb_file(temp_url, vid_path, crop=True, quality=quality, check_404=True):
                # Got 404 image, try lower quality... Oh wait there is none! uh-oh....
                logger.error("ERROR: force_download_best() tried to go lower than 'default' quality!")
                break


def crop_blackbars(image_filename, quality):
    """
    Crop certain thumbnails that come shipped with black bars above and under
    Qualities affected by this affliction, and actions taken:
        high:       480x360 with bars --> crop to 480x270
        standard:   640x480 with bars --> crop to 640x360
        default:    120x90  with bars --> crop to 120x68

    coords: A tuple of x/y coordinates (x1, y1, x2, y2) or (left, top, right, bottom)
    :param image_filename:
    :param quality:
    :return:
    """

    img = Image.open(image_filename)
    coords = None
    if quality == 'standard':
        coords = (0, 60, 640, (480 - 60))
    elif quality == 'high':
        coords = (0, 45, 480, (360 - 45))
    elif quality == 'default':
        coords = (0, 11, 120, (90 - 11))
    cropped_img = img.crop(coords)
    cropped_img.save(os.path.join(THUMBNAILS_PATH, image_filename))


def quality_404_check(img):
    """
    Checks if the given image matches the YouTube 404: Thumbnail not found image
    :param img:
    :return: True if given image equals YouTube's 404 image
    """
    img_404 = Image.open(THUMBNAIL_404_PATH)
    img_cmp = Image.open(img)
    check = ImageChops.difference(img_cmp, img_404).getbbox() is None
    return check


def resize_thumbnail(img_path, maxwidth, maxheight, out=True):
    """
    Resizes and antialises thumbnail up to the given maximum size, thus maintaining AR

    https://pillow.readthedocs.io/en/3.0.x/releasenotes/2.7.0.html#default-filter-for-thumbnails
    :param out:
    :param maxheight: int
    :param maxwidth: int
    :param img_path: string/path
    :return: resized image or 404 image if operation failed
    """
    if img_path is None:
        img_path = THUMBNAIL_NA_PATH
    outdir = THUMBNAILS_RESIZED_PATH
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    im = Image.open(img_path)
    resize_ratio = min(maxwidth / im.width, maxheight / im.height)
    new_size = tuple(int(resize_ratio * x) for x in im.size)
    try:
        im.thumbnail(new_size, Image.BICUBIC)
        if out:
            outfile_path = os.path.join(outdir, img_path[-15:])
            im.save(outfile_path)
            return outfile_path
        elif out is False:
            return im
    except IOError as eio:
        logger.error("Cannot create thumbnail for {}: IOError".format(img_path))
        logger.exception(eio)
        logger.info("Returning default 'Thumbnail N/A' image")
        return Image.open(THUMBNAIL_NA_PATH)
