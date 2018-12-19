from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from sane_yt_subfeed import create_logger
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
    subscribed = Column(Boolean)
    subscribed_override = Column(Boolean)

    tests = relationship('Test', back_populates='channel')
    costs = relationship('RunCost', back_populates='channel')

    def __init__(self, youtube_response, playlist_id, channel_list_response=False):
        self.logger = create_logger(__name__)
        if channel_list_response:
            self.id = youtube_response['id']  # channelList response id is outside of snippet section
            youtube_response = youtube_response['snippet']  # Readjust to same level as subscriptionList response
        else:
            self.id = youtube_response['resourceId']['channelId']

        try:
            self.title = youtube_response['title']
        except KeyError as ke_exc_title:
            self.logger.error("DB <--: Failed getting title key from YouTube response! Setting value to: None",
                              exc_info=ke_exc_title)
            self.logger.debug(youtube_response)
            # raise ke_exc_title
            self.title = None
        try:
            self.description = youtube_response['description']
        except KeyError as ke_exc_desc:
            self.logger.error("DB <--: failed getting description key from YouTube response!! Setting value to: None",
                              exc_info=ke_exc_desc)
            self.logger.debug(youtube_response)
            # raise ke_exc_desc
            self.description = None
        try:
            self.thumbnails = youtube_response['thumbnails']
        except KeyError as ke_exc_thumbs:
            self.logger.error("DB <--: failed getting thumbnails key from YouTube response!! Setting value to: None",
                              exc_info=ke_exc_thumbs)
            self.logger.debug(youtube_response)
            # raise ke_exc_thumbs
            self.thumbnails = None

        self.snippet = youtube_response
        self.playlist_id = playlist_id
        self.subscribed = True
        self.subscribed_override = False


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
