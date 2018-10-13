import datetime

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.settings import YOUTUBE_URL_BASE, YOUTUBE_URL_PART_VIDEO

GRAB_METHOD_LIST = 'list()'
GRAB_METHOD_SEARCH = 'search()'
GRAB_METHOD_VIDEOS = 'videos()'


class VideoD:
    thumbnail_path = ""
    playlist_pos = None
    url_playlist_video = None
    discarded = False
    new = False
    missed = False
    watch_prio = read_config('Play', 'default_watch_prio')

    def __init__(self, search_item, grab_methods=None):
        """
        Creates a Video object from a YouTube playlist_item
        :param search_item:
        """
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
            self.duration = None
            return

        self.video_id = search_item['id']['videoId']
        self.channel_title = search_item['snippet']['channelTitle']
        self.title = search_item['snippet']['title']
        str_date = search_item['snippet']['publishedAt']
        self.date_published = datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.000Z')
        self.description = search_item['snippet']['description']
        self.channel_id = search_item['snippet']['channelId']

        self.url_video = YOUTUBE_URL_BASE + YOUTUBE_URL_PART_VIDEO + self.video_id
        self.thumbnails = search_item['snippet']['thumbnails']
        self.search_item = search_item
        self.watched = False


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
