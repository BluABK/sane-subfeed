import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Column, Integer, String

from sane_yt_subfeed.database.decorators import TextPickleType
from sane_yt_subfeed.settings import YOUTUBE_URL_BASE, YOUTUBE_URL_PART_VIDEO
from sane_yt_subfeed.database.orm import PermanentBase


class Video(PermanentBase):
    __tablename__ = 'video'
    video_id = Column('video_id', String, primary_key=True)
    channel_title = Column(String)
    title = Column(String)
    playlist_id = Column(String)
    date_published = Column(DateTime)
    description = Column(String)
    thumbnail_path = Column(String)
    playlist_pos = Column(String)
    url_video = Column(String)
    url_playlist_video = Column(String)
    stats_time_elapsed = Column(String)
    thumbnails = Column(TextPickleType())
    downloaded = Column(Boolean)
    search_item = Column(TextPickleType())

    def __init__(self, search_item):
        """
        Creates a Video object from a YouTube playlist_item
        :param search_item:
        """
        self.video_id = search_item['id']['videoId']
        self.channel_title = search_item['snippet']['channelTitle']
        self.title = search_item['snippet']['title']
        str_date = search_item['snippet']['publishedAt']
        self.date_published = datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.000Z')
        self.description = search_item['snippet']['description']
        # self.playlist_id = search_item['snippet']['playlistId']   # Which playlist it's added from
        # self.playlist_pos = search_item['snippet']['position']    # Which position it's got in the playlist
        self.channel_id = search_item['snippet']['channelId']

        self.url_video = YOUTUBE_URL_BASE + YOUTUBE_URL_PART_VIDEO + self.video_id
        # self.url_playlist_video = self.url_video + "&list=" + self.playlist_id
        self.downloaded = False
        self.thumbnails = search_item['snippet']['thumbnails']
        self.search_item = search_item
        # self.determine_thumbnails(playlist_item.snippet.thumbnails)

    def determine_thumbnails(self, thumbnails_item):
        """
        Takes a youtube#playListItem thumbnails section and determines which qualities are available.

        This is required since YouTube supplies an unpredictable set of thumbnail qualities.
        :param thumbnails_item:
        :return:
        """
        self.thumbnails['available_quality'] = []
        # Check which quality thumbnails actually exist for this video
        if 'default' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("default")  # 120x90 px
            self.thumbnails['default'] = thumbnails_item['default']
        if 'medium' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("medium")  # 320x180 px
            self.thumbnails['medium'] = thumbnails_item['medium']
        if 'high' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("high")  # 480x360 px
            self.thumbnails['high'] = thumbnails_item['high']
        if 'standard' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("standard")  # 640x480 px
            self.thumbnails['standard'] = thumbnails_item['standard']
        if 'maxres' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("maxres")  # 1280x720 px
            self.thumbnails['maxres'] = thumbnails_item['maxres']

    def to_video_d(self):
        video_d = Video(self.search_item)
        video_d.downloaded = self.downloaded
        video_d.thumbnail_path = self.thumbnail_path
        return video_d

    def video_d_update(self, video_d):
        self.thumbnail_path = video_d.thumbnail_path
        self.downloaded = video_d.downloaded
