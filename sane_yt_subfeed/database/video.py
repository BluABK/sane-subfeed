import datetime
from sqlalchemy import Boolean, DateTime, Column, Integer, String, Interval

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.decorators import TextPickleType
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.orm import PermanentBase
from sane_yt_subfeed.settings import YOUTUBE_URL_BASE, YOUTUBE_URL_PART_VIDEO


class Video(PermanentBase):  # FIXME: PickleTypes should probably be replaced by actual tables
    """
    Video SQLAlchemy Database table object

    For info on various columns see https://developers.google.com/youtube/v3/docs/videos
    """
    __tablename__ = 'video'
    video_id = Column('video_id', String, primary_key=True)
    channel_title = Column(String)
    title = Column(String)
    date_published = Column(DateTime)
    date_downloaded = Column(DateTime)
    description = Column(String)
    thumbnail_path = Column(String)
    playlist_pos = Column(String)
    url_video = Column(String)
    url_playlist_video = Column(String)
    thumbnails = Column(TextPickleType())
    downloaded = Column(Boolean)
    discarded = Column(Boolean)
    search_item = Column(TextPickleType())
    vid_path = Column(String)
    watched = Column(Boolean)
    watch_prio = Column(Integer)
    duration = Column(Interval)
    has_caption = Column(Boolean)
    dimension = Column(String)
    definition = Column(String)
    projection = Column(String)
    region_restriction_allowed = Column(TextPickleType())
    region_restriction_blocked = Column(TextPickleType())

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
        self.channel_id = search_item['snippet']['channelId']

        self.url_video = YOUTUBE_URL_BASE + YOUTUBE_URL_PART_VIDEO + self.video_id
        self.downloaded = False
        self.thumbnails = search_item['snippet']['thumbnails']
        self.search_item = search_item
        self.watched = False
        self.watch_prio = read_config('Play', 'default_watch_prio')

    def __str__(self):
        """
        Override __str__ to print a more sensible string.
        :return:
        """
        return "{} - {} [{}]".format(self.channel_title, self.title, self.url_video)

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

    @staticmethod
    def to_video_d(video):
        video_d = VideoD(video.search_item)
        video_d.downloaded = video.downloaded
        video_d.thumbnail_path = video.thumbnail_path
        video_d.discarded = video.discarded
        video_d.vid_path = video.vid_path
        video_d.watched = video.watched
        video_d.watch_prio = video.watch_prio
        video_d.date_downloaded = video.date_downloaded
        video_d.duration = video.duration
        video_d.has_caption = video.has_caption
        video_d.dimension = video.dimension
        video_d.definition = video.definition
        video_d.projection = video.projection
        video_d.region_restriction_allowed = video.region_restriction_allowed
        video_d.region_restriction_blocked = video.region_restriction_blocked
        return video_d

    @staticmethod
    def to_video_ds(videos):
        video_ds = []
        for video in videos:
            video_ds.append(Video.to_video_d(video))
        return video_ds

    def video_d_update(self, video_d):
        self.thumbnail_path = video_d.thumbnail_path
        self.downloaded = video_d.downloaded
        self.discarded = video_d.discarded
        self.vid_path = video_d.vid_path
        self.watched = video_d.watched
        self.watch_prio = video_d.watch_prio
        self.date_downloaded = video_d.date_downloaded
        self.duration = video_d.duration
        self.has_caption = video_d.has_caption
        self.dimension = video_d.dimension
        self.definition = video_d.definition
        self.projection = video_d.projection
        self.region_restriction_allowed = video_d.region_restriction_allowed
        self.region_restriction_blocked = video_d.region_restriction_blocked

    @staticmethod
    def video_d_to_video(video_d):
        video = Video(video_d.search_item)
        video.downloaded = video_d.downloaded
        video.thumbnail_path = video_d.thumbnail_path
        video.discarded = video_d.discarded
        video.vid_path = video_d.vid_path
        video.watched = video_d.watched
        video.watch_prio = video_d.watch_prio
        video.date_downloaded = video_d.date_downloaded
        video.duration = video_d.duration
        video.has_caption = video_d.has_caption
        video.dimension = video_d.dimension
        video.definition = video_d.definition
        video.projection = video_d.projection
        video.region_restriction_allowed = video_d.region_restriction_allowed
        video.region_restriction_blocked = video_d.region_restriction_blocked
        return video
