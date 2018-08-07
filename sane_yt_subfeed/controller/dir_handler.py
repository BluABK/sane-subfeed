import datetime
import os
import threading
from watchdog.events import PatternMatchingEventHandler

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.read_operations import get_videos_by_ids, get_vid_by_id
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded
from sane_yt_subfeed.youtube.update_videos import load_keys
from sane_yt_subfeed.youtube.youtube_requests import list_uploaded_videos_videos

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)


def get_yt_file(search_path, id):
    for name in os.listdir(search_path):
        if id in name:
            return name
    return None


class VidEventHandler(PatternMatchingEventHandler):
    patterns = ["*.mp4", "*.webm", "*.mkv"]

    def __init__(self, listener):
        super().__init__()
        self.listener = listener

    # def on_any_event(self, event):
    #     print("change")
    #     if event.event_type == 'created':
    #         f = open(event.src_path, encoding="utf-8")
    #         tags = exifread.process_file(f)
    #         # img = Image.open(event.src_path)
    #         time.sleep(1)

    # def on_modified(self, event):
    #     print("change")
    #     # self.process(event)

    def on_created(self, event):
        if not event.src_path:
            return
        split_string = "_v-id-"
        if split_string in event.src_path:
            logger.info("Discovered new file")
            name = os.path.basename(event.src_path)
            filename = name.split(".")
            for s in filename:
                if split_string in s:
                    filename = str(s)
            id = str(filename.split(split_string)[-1])
            self.listener.newFile.emit(id, event.src_path)


def manual_youtube_folder_check(input_path):
    # input_path = os.path.join(OS_PATH, input_folder)

    vid_paths = {}
    # start_time = timeit.default_timer()
    split_string = "_v-id-"
    for name in os.listdir(input_path):
        if split_string in name:
            filename = name.split(".")
            for s in filename:
                if split_string in s:
                    filename = str(s)
            id = str(filename.split(split_string)[-1])
            vid_paths[id] = os.path.join(input_path, name)

    return_videos = get_new_and_updated_videos(vid_paths)

    return return_videos
    # print(timeit.default_timer() - start_time)


def get_new_and_updated_videos(vid_paths):
    """
    :param vid_paths: dict(video_id, vid_path)
    :return:
    """
    db_videos = get_videos_by_ids(vid_paths.keys())

    return_videos = []
    for video in db_videos:
        if not video.downloaded:
            video_d = Video.to_video_d(video)
            video_d.vid_path = vid_paths[video.video_id]
            video_d.downloaded = True
            video_d.date_downloaded = datetime.datetime.utcnow()

            return_videos.append(video_d)
        vid_paths.pop(video.video_id, None)

    new_videos = []
    if len(vid_paths) > 0:
        youtube_keys = load_keys(1)
        response_videos = list_uploaded_videos_videos(youtube_keys[0], vid_paths.keys(), 30)
        for video in response_videos:
            video.vid_path = vid_paths[video.video_id]
            video.downloaded = True
            video.date_downloaded = datetime.datetime.utcnow()
            new_videos.append(video)
        logger.info("Grabbing new video(s) information from youtube")
        download_thumbnails_threaded(new_videos)

    return_videos.extend(new_videos)
    return return_videos


class CheckYoutubeFolderForNew(threading.Thread):

    def __init__(self, input_path, db_listeners=None):
        threading.Thread.__init__(self)
        self.input_path = input_path
        self.db_listeners = db_listeners

    def run(self):
        logger.debug("Starting CheckYoutubeFolderForNew thread")
        videos = manual_youtube_folder_check(self.input_path)
        UpdateVideosThread(videos, update_existing=True, finished_listeners=self.db_listeners).start()
