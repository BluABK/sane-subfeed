import time

import datetime
import threading
from PyQt5.QtCore import QObject, pyqtSignal
from sqlalchemy import false

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners import static_listeners
from sane_yt_subfeed.database.db_download_tile import DBDownloadTile
from sane_yt_subfeed.database.detached_models.d_db_download_tile import DDBDownloadTile
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.write_operations import UpdateVideo, update_event_download_tile, lock
from sane_yt_subfeed.youtube.youtube_dl_handler import YoutubeDownload


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
    updateDownloadTileEvent = pyqtSignal(DDBDownloadTile)
    updateDownloadTile = pyqtSignal(DDBDownloadTile)

    def __init__(self, main_model):
        super(DownloadHandler, self).__init__()
        DownloadHandler.static_self = self
        self.logger = create_logger(__name__ + ".DownloadHandler")

        self.main_model = main_model
        self.loadDBDownloadTiles.connect(self.load_db_download_tiles)
        self.newDownloadTile.connect(self.new_download_tile)
        self.updateDownloadTileEvent.connect(self.update_download_tile_event)
        self.updateDownloadTile.connect(self.update_download_tile)

    def run(self):
        while True:
            time.sleep(2)

    def update_download_tile(self, download_tile):
        result = db_session.query(DBDownloadTile).filter(
            DBDownloadTile.video_id == format(download_tile.video.video_id)).first()
        # stmt = DBDownloadTile.__table__.select().where(
        #     text("video_id = '{}'".format(download_tile.video.video_id)))
        # result = engine.execute(stmt).first()
        if result:
            result.update_tile(download_tile)
            db_session.commit()
            db_session.remove()
        else:
            self.logger.warning(
                "Download tile not found in db, so no update was performed: {}".format(download_tile.__dict__))

    @staticmethod
    def update_download_tile_event(download_tile):
        update_event_download_tile(download_tile)

    def new_download_tile(self, new_tile):
        lock.acquire()
        result = db_session.query(DBDownloadTile).filter(
            DBDownloadTile.video_id == format(new_tile.video.video_id)).first()
        if not result:
            download_tile = DBDownloadTile(new_tile)
            if not download_tile.video:
                self.logger.error("No video in new tile: {}".format(download_tile.__dict__), exc_info=True)
                return
            db_session.add(download_tile)
            db_session.commit()
        db_session.remove()
        lock.release()

    def load_db_download_tiles(self):
        db_result = db_session.query(DBDownloadTile).filter(DBDownloadTile.cleared == false()).all()
        detached_db_result = DDBDownloadTile.list_detach(db_result)
        use_youtube_dl = read_config('Youtube-dl', 'use_youtube_dl')
        download_finished_signals = [static_listeners.STATIC_GRID_VIEW_LISTENER.downloadFinished]
        for tile in detached_db_result:
            if use_youtube_dl and not tile.finished:
                self.logger.info("Starting paused in progress download for: {}".format(tile.video.__dict__))
                tile.progress_listener = \
                    DownloadHandler.download_using_youtube_dl(tile.video,
                                                              youtube_dl_finished_listener=download_finished_signals,
                                                              wait=True)
        self.dbDownloadTiles.emit(detached_db_result)

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
