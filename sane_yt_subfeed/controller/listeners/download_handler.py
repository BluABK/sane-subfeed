import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from sane_yt_subfeed.youtube.youtube_dl_handler import YoutubeDownload

from sane_yt_subfeed.database.write_operations import UpdateVideo

from sane_yt_subfeed.config_handler import read_config


class DownloadProgressSignals(QObject):
    updateProgress = pyqtSignal(dict)

    def __init__(self, video):
        super(DownloadProgressSignals, self).__init__()
        self.video = video


class DownloadHandler(QObject):
    static_self = None

    newYTDLDownlaod = pyqtSignal(DownloadProgressSignals)

    def __init__(self):
        super(DownloadHandler, self).__init__()
        DownloadHandler.static_self = self

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
                            finished_listener=youtube_dl_finished_listener).start()
