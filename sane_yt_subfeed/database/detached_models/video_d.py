import datetime

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.constants import YOUTUBE_URL_BASE, YOUTUBE_URL_PART_VIDEO

GRAB_METHOD_LIST = 'list()'
GRAB_METHOD_SEARCH = 'search()'
GRAB_METHOD_VIDEOS = 'videos()'
VIDEO_KIND_VOD = 100
VIDEO_KIND_LIVE = 200
VIDEO_KIND_LIVE_SCHEDULED = 201
VIDEO_KIND_PREMIERE = 300


class VideoD:
    thumbnail_path = ""
    playlist_pos = None
    url_playlist_video = None
    discarded = False
    new = False
    missed = False
    watch_prio = read_config('Play', 'default_watch_prio')

    def __init__(self, search_item, grab_methods=None, kind=VIDEO_KIND_VOD):
        """
        Creates a Video object from a YouTube playlist_item
        :param search_item: A raw YouTube API search()/list() JSON Snippet
        """
        self.logger = create_logger(__name__)
        self.grab_methods = []
        self.vid_path = ""
        self.date_downloaded = None
        self.duration = None
        self.has_caption = False
        self.downloaded = False
        self.dimension = ""
        self.definition = ""
        self.projection = ""
        self.region_restriction_allowed = []
        self.region_restriction_blocked = []
        self.kind = kind  # Assume VOD by default.

        # Put liveBroadcastContent at start of feed to avoid it being buried.
        if self.kind == VIDEO_KIND_LIVE:
            self.watch_prio = 0
        elif self.kind == VIDEO_KIND_LIVE_SCHEDULED:
            self.watch_prio = 1
        elif self.kind == VIDEO_KIND_PREMIERE:
            self.watch_prio = 2

        if grab_methods is None:
            grab_methods = []

        # TODO: add to Video
        if grab_methods:
            self.grab_methods = grab_methods

        if not search_item:
            self.video_id = ""
            self.channel_title = ""
            self.title = ""
            self.date_published = datetime.datetime.utcnow()
            self.description = ""
            self.channel_id = ""

            self.url_video = ""
            self.thumbnails = ""
            self.search_item = ""
            self.watched = False
            return
        try:
            self.video_id = search_item['id']['videoId']
        except Exception as anomaly:
            self.logger.exception("Exception while creating VideoD obj!", exc_info=anomaly)
            self.logger.info(search_item)
            raise
        self.channel_title = search_item['snippet']['channelTitle']
        self.title = search_item['snippet']['title']
        str_date = search_item['snippet']['publishedAt']
        self.date_published = datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.000Z')
        self.description = search_item['snippet']['description']
        self.channel_id = search_item['snippet']['channelId']

        self.url_video = YOUTUBE_URL_BASE + YOUTUBE_URL_PART_VIDEO + self.video_id
        if 'thumbnails' in search_item['snippet']:
            self.thumbnails = search_item['snippet']['thumbnails']
        else:
            self.logger.critical("No thumbnails key in snippet!")
            self.logger.error(search_item)
            self.thumbnails = None
        self.search_item = search_item
        self.watched = False

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
    def playlist_item_new_video_d(playlist_item, grab_methods=None):
        playlist_item['id'] = playlist_item['snippet']['resourceId']
        return VideoD(playlist_item, grab_methods=grab_methods)

    @staticmethod
    def videos_item_new_video_d(videos_item, grab_methods=None):
        videos_item['id'] = {'videoId': videos_item['id']}
        return VideoD(videos_item, grab_methods=grab_methods)
