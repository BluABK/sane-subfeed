import datetime
import time

from PyQt5.QtCore import QObject, pyqtSignal
from sqlalchemy import false

from sane_yt_subfeed.database.db_download_tile import DBDownloadTile
from sane_yt_subfeed.database.detached_models.d_db_download_tile.db_download_tile import DDBDownloadTile
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.youtube.youtube_dl_handler import YoutubeDownload

from sane_yt_subfeed.database.write_operations import UpdateVideo

from sane_yt_subfeed.config_handler import read_config


class DownloadProgressSignals(QObject):
    updateProgress = pyqtSignal(dict)
    finishedDownload = pyqtSignal()

    def __init__(self, video):
        super(DownloadProgressSignals, self).__init__()
        self.video = video


class DownloadHandler(QObject):
    static_self = None

    newYTDLDownlaod = pyqtSignal(DownloadProgressSignals)
    loadDBDownloadTiles = pyqtSignal()
    dbDownloadTiles = pyqtSignal(list)
    newDownloadTile = pyqtSignal()

    def __init__(self, main_model):
        super(DownloadHandler, self).__init__()
        DownloadHandler.static_self = self
        self.main_model = main_model
        self.loadDBDownloadTiles.connect(self.load_db_download_tiles)

    def run(self):
        while True:
            time.sleep(2)

    def load_db_download_tiles(self):
        db_result = db_session.query(DBDownloadTile).filter(DBDownloadTile.cleared == false()).all()
        DDBDownloadTile.list_detach(db_result)
        self.dbDownloadTiles.emit(db_result)

    @staticmethod
    def download_video(video, db_update_listeners=None, youtube_dl_finished_listener=None):
        use_youtube_dl = read_config('Youtube-dl', 'use_youtube_dl')
        video.downloaded = True
        video.date_downloaded = datetime.datetime.utcnow()
        UpdateVideo(video, update_existing=True,
                    finished_listeners=db_update_listeners).start()
        if use_youtube_dl:
            download_progress_signal = DownloadProgressSignals(video)
            DownloadHandler.static_self.newYTDLDownlaod.emit(download_progress_signal)
            YoutubeDownload(video, download_progress_listener=download_progress_signal,
                            finished_listeners=youtube_dl_finished_listener).start()
