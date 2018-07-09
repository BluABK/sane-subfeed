from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
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

    tests = relationship('Test', back_populates='channel')
    costs = relationship('RunCost', back_populates='channel')

    def __init__(self, youtube_response):
        self.id = youtube_response['resourceId']['channelId']
        self.title = youtube_response['title']
        self.description = youtube_response['description']
        self.thumbnails = youtube_response['thumbnails']
        self.snippet = youtube_response


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

