from sane_yt_subfeed.database.video import Video


class DDBDownloadTile:

    def __init__(self, download_tile, db_download_tile=False):
        self.finished = download_tile.finished
        self.started_date = download_tile.started_date
        self.finished_date = download_tile.finished_date
        if db_download_tile:
            self.video = Video.to_video_d(download_tile.video)
        else:
            self.video = download_tile.video
        self.video_downloaded = download_tile.video_downloaded
        self.total_bytes = download_tile.total_bytes
        self.last_event = download_tile.last_event
        self.cleared = download_tile.cleared

        # Other
        self.progress_listener = None

    @staticmethod
    def list_detach(download_tile_list):
        return_list = []
        for download_tile in download_tile_list:
            return_list.append(DDBDownloadTile(download_tile, db_download_tile=True))
        return return_list
