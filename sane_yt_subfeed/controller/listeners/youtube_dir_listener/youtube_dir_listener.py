import time

import datetime
import os
from PyQt5.QtCore import *
from watchdog.observers import Observer

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.controller.dir_handler import VidEventHandler, CheckYoutubeFolderForNew
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideo
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded, THUMBNAILS_PATH
from sane_yt_subfeed.youtube.update_videos import load_keys
from sane_yt_subfeed.youtube.youtube_requests import list_uploaded_videos_videos


class YoutubeDirListener(QObject):
    newFile = pyqtSignal(str, str)
    manualCheck = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.logger = create_logger(__name__ + '.YoutubeDirListener')
        self.model = model

        self.newFile.connect(self.new_file)
        self.manualCheck.connect(self.manual_check)

        disable_dir_observer = read_config('Play', 'disable_dir_listener')
        if not disable_dir_observer:
            path = read_config('Play', 'yt_file_path', literal_eval=False)
            event_handler = VidEventHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, path)
            self.observer.start()

    def run(self):
        while True:
            time.sleep(2)

    @pyqtSlot(str, str)
    def new_file(self, vid_id, vid_path):
        vid = db_session.query(Video).get(vid_id)
        if vid:
            if not vid.downloaded:
                vid.vid_path = vid_path
                vid.date_downloaded = datetime.datetime.utcnow()
                vid.downloaded = True

                thumb_path = os.path.join(THUMBNAILS_PATH, '{}.jpg'.format(vid.video_id))
                downloaded_thumbnail = os.path.isfile(thumb_path)
                if downloaded_thumbnail and (not vid.thumbnail_path):
                    vid.thumbnail_path = thumb_path
                    self.logger.warning(
                        "Thumbnail downloaded, but path didn't exist in db, for video: {}".format(vid.__dict__))
                elif (not vid.thumbnail_path) or (not downloaded_thumbnail):
                    if not downloaded_thumbnail:
                        self.logger.warning("Thumbnail path in db, but not on disk, for video: {}".format(vid.__dict__))
                    self.logger.info("Downloading thumbnail for: {}".format(vid.__dict__))
                    download_thumbnails_threaded([vid])

                self.logger.info("Updating existing record in db: {} - {}".format(vid.title, vid.__dict__))
                db_session.commit()
                self.model.update_subfeed_videos_from_db()
                self.model.update_playback_videos_from_db()
            else:
                self.logger.info("File already downloaded by this system: {} - {}".format(vid.title, vid.__dict__))
            db_session.remove()

        else:
            db_session.remove()
            youtube_keys = load_keys(1)
            self.logger.info("Grabbing new video information from youtube: {}".format(vid_id))
            response_videos = list_uploaded_videos_videos(youtube_keys[0], [vid_id], 1)
            if len(response_videos) > 0:
                video = response_videos[0]
                video.vid_path = vid_path
                video.downloaded = True
                video.watched = False
                video.date_downloaded = datetime.datetime.utcnow()
                self.logger.info("Downloading thumbnail: {} - {}".format(video.title, video.__dict__))
                download_thumbnails_threaded([video])
                self.logger.info("Adding new file to db: {} - {}".format(video.title, video.__dict__))
                UpdateVideo(video,
                            finished_listeners=[
                                self.model.playback_grid_view_listener.downloadedVideosChangedinDB]).start()
            else:
                self.logger.warning("Video with id {}, not found on youtube servers".format(vid_id))

    @pyqtSlot()
    def manual_check(self):
        youtube_folder = read_config("Play", "yt_file_path", literal_eval=False)
        CheckYoutubeFolderForNew(youtube_folder,
                                 db_listeners=[self.model.playback_grid_view_listener.downloadedVideosChangedinDB,
                                               self.model.playback_grid_view_listener.updateGridViewFromDb]).start()
