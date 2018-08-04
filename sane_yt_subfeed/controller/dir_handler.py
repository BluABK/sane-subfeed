import datetime
import os
import threading
import time
import timeit
import ffmpeg
from watchdog.events import PatternMatchingEventHandler

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.read_operations import get_videos_by_ids
from sane_yt_subfeed.database.write_operations import UpdateVideosThread


def get_yt_file(search_path, id):
    for name in os.listdir(search_path):
        if id in name:
            return name
    return None


class VidEventHandler(PatternMatchingEventHandler):
    patterns = ["*.mp4", "*.webm"]

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

        try:
            file = ffmpeg.probe(event.src_path)
            try:
                yt_comment = file['format']['tags']['comment']
                vid_id = yt_comment.split('v=')[-1]
                self.listener.newFile.emit(vid_id, event.src_path)
            except Exception as e:
                raise e

        except Exception as e:
            print("Trying to probe file again")
            time.sleep(0.3)
            self.on_created(event)


def manual_youtube_folder_check(input_path):
    # input_path = os.path.join(OS_PATH, input_folder)

    video_ids = []
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
            video_ids.append(id)
            vid_paths[id] = os.path.join(input_path, name)
    return_videos = get_videos_by_ids(video_ids)
    for video in return_videos:
        video.vid_path = vid_paths[video.video_id]

    return return_videos
    # print(timeit.default_timer() - start_time)


class CheckYoutubeFolderForNew(threading.Thread):

    def __init__(self, input_path, db_listener=None):
        threading.Thread.__init__(self)
        self.input_path = input_path
        self.db_listener = db_listener

    def run(self):
        videos = manual_youtube_folder_check(self.input_path)
        for video in videos:
            video.downloaded = True
            video.date_downloaded = datetime.datetime.utcnow()
        UpdateVideosThread(videos, update_existing=True, finished_listener=self.db_listener).start()

if __name__ == '__main__':
    path = read_config('Play', 'yt_file_path', literal_eval=False)
    manual_youtube_folder_check(path)
