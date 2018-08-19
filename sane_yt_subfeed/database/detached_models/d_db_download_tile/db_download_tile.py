from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from sane_yt_subfeed.database.decorators import TextPickleType
from sane_yt_subfeed.database.orm import PermanentBase


class DDBDownloadTile:

    def __init__(self, download_tile):
        self.finished = download_tile.finished
        self.started_date = download_tile.started_date
        self.finished_date = download_tile.finished_date
        self.video = download_tile.video
        self.video_downloaded = download_tile.video_downloaded
        self.total_bytes = download_tile.total_bytes
        self.last_event = download_tile.last_event
        self.cleared = download_tile.cleared

    @staticmethod
    def list_detach(download_tile_list):
        return_list = []
        for download_tile in download_tile_list:
            return_list.append(DDBDownloadTile(download_tile))
        return return_list
