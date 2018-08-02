import os
import sys
import time
import timeit
import ffmpeg
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video


def get_yt_file(search_path, id):
    for name in os.listdir(search_path):
        if id in name:
            return name
    return None

class VidEventHandler(PatternMatchingEventHandler):
    patterns = ["*.mp4"]

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
        try:
            file = ffmpeg.probe(event.src_path)
            yt_comment = file['format']['tags']['comment']
            vid_id = yt_comment.split('v=')[-1]
            self.listener.newFile.emit(vid_id, event.src_path)

        except Exception as e:
            print("Trying to probe file again")
            time.sleep(0.3)
            self.on_created(event)
