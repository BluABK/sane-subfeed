import datetime
import threading
import time

from PyQt5.QtCore import QObject, pyqtSignal
from sqlalchemy import false

from sane_yt_subfeed.database.db_download_tile import DBDownloadTile
from sane_yt_subfeed.database.detached_models.d_db_download_tile import DDBDownloadTile
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.youtube.youtube_dl_handler import YoutubeDownload

from sane_yt_subfeed.database.write_operations import UpdateVideo

from sane_yt_subfeed.config_handler import read_config


class DownloadProgressSignals(QObject):
    updateProgress = pyqtSignal(dict)
    finishedDownload = pyqtSignal()

    def __init__(self, video, threading_event):
        super(DownloadProgressSignals, self).__init__()
        self.video = video
        self.threading_event = threading_event


class DownloadHandler(QObject):
    static_self = None

    newYTDLDownlaod = pyqtSignal(DownloadProgressSignals)
    loadDBDownloadTiles = pyqtSignal()
    dbDownloadTiles = pyqtSignal(list)
    newDownloadTile = pyqtSignal(DDBDownloadTile)

    def __init__(self, main_model):
        super(DownloadHandler, self).__init__()
        DownloadHandler.static_self = self
        self.main_model = main_model
        self.loadDBDownloadTiles.connect(self.load_db_download_tiles)
        self.newDownloadTile.connect(self.new_download_tile)

    def run(self):
        while True:
            time.sleep(2)

    def new_download_tile(self, new_tile):
        result = db_session.query(DBDownloadTile).filter(
            DBDownloadTile.video_id == new_tile.video.video_id).first()
        if not result:
            db_session.add(DBDownloadTile(new_tile))
            db_session.commit()
        db_session.remove()

    def load_db_download_tiles(self):
        db_result = db_session.query(DBDownloadTile).filter(DBDownloadTile.cleared == false()).all()
        detached_db_result = DDBDownloadTile.list_detach(db_result)
        use_youtube_dl = read_config('Youtube-dl', 'use_youtube_dl')
        return_listeners = []
        for tile in detached_db_result:
            if use_youtube_dl:
                return_listeners.append(DownloadHandler.download_using_youtube_dl(tile.video, wait=True))
        self.dbDownloadTiles.emit(return_listeners)

    @staticmethod
    def download_video(video, db_update_listeners=None, youtube_dl_finished_listener=None):
        use_youtube_dl = read_config('Youtube-dl', 'use_youtube_dl')
        video.downloaded = True
        video.date_downloaded = datetime.datetime.utcnow()
        UpdateVideo(video, update_existing=True,
                    finished_listeners=db_update_listeners).start()
        if use_youtube_dl:
            download_progress_signal = DownloadHandler.download_using_youtube_dl(video, youtube_dl_finished_listener)
            DownloadHandler.static_self.newYTDLDownlaod.emit(download_progress_signal)

    @staticmethod
    def download_using_youtube_dl(video, youtube_dl_finished_listener=None, wait=False):
        event = threading.Event()
        if not wait:
            event.set()
        download_progress_signal = DownloadProgressSignals(video, event)
        YoutubeDownload(video, event, download_progress_listener=download_progress_signal,
                        finished_listeners=youtube_dl_finished_listener).start()
        return download_progress_signal
