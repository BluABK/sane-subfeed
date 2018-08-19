from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from sane_yt_subfeed.database.decorators import TextPickleType
from sane_yt_subfeed.database.orm import PermanentBase


class Channel(PermanentBase):
    __tablename__ = 'channel'
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    downloaded_thumbnail = Column(String)
    thumbnails = Column(TextPickleType())
    snippet = Column(TextPickleType)
    playlist_id = Column(String)

    tests = relationship('Test', back_populates='channel')
    costs = relationship('RunCost', back_populates='channel')

    def __init__(self, youtube_response, playlist_id):
        self.id = youtube_response['resourceId']['channelId']
        self.title = youtube_response['title']
        self.description = youtube_response['description']
        self.thumbnails = youtube_response['thumbnails']
        self.snippet = youtube_response
        self.playlist_id = playlist_id


class Test(PermanentBase):
    __tablename__ = 'test'
    id = Column('id', Integer, primary_key=True)
    date = Column(DateTime)
    test_pages = Column(Integer)
    test_miss = Column(Integer)
    channel_id = Column(String, ForeignKey('channel.id'))
    channel = relationship('Channel', back_populates='tests')

    def __init__(self, date, test_pages, test_miss, channel):
        self.date = date
        self.test_pages = test_pages
        self.test_miss = test_miss
        self.channel = channel


class RunCost(PermanentBase):
    __tablename__ = 'run_cost'
    id = Column('id', Integer, primary_key=True)
    date = Column(DateTime)
    quota_cost = Column(Integer)
    requests = Column(Integer)
    channel_id = Column(String, ForeignKey('channel.id'))
    channel = relationship('Channel', back_populates='costs')

    def __init__(self, date, quota_cost, requests):
        self.date = date
        self.quota_cost = quota_cost
        self.requests = requests


class DownloadTile(PermanentBase):
    __tablename__ = 'download_tile'
    id = Column('id', Integer, primary_key=True)
    finished = Column(Boolean)
    started_date = Column(DateTime)
    finished_date = Column(DateTime)
    video_id = Column(String, ForeignKey('video.video_id'))
    video = relationship('Video')
    video_downloaded = Column(Boolean)
    total_bytes = Column(Integer)
    last_event = Column(TextPickleType())

    def __init__(self, download_tile):
        self.finished = download_tile.finished
        self.started_date = download_tile.started_date
        self.finished_date = download_tile.finished_date
        self.video = download_tile.video
        self.video_downloaded = download_tile.video_downloaded
        self.total_bytes = download_tile.total_bytes
        self.last_event = download_tile.last_event
