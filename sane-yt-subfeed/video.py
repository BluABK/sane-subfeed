from settings import YOUTUBE_URL_BASE, YOUTUBE_URL_PART_VIDEO


class Video:
    channel_title = None
    title = None
    video_id = None
    date_published = None
    description = None
    thumbnails = {}
    playlist_id = None
    playlist_pos = None
    url_video = None
    url_playlist_video = None
    stats_time_elapsed = None

    def __init__(self, playlist_item):
        """
        Creates a Video object from a YouTube playlist_item
        :param playlist_item:
        """
        self.channel_title = playlist_item['snippet']['channelTitle']
        self.title = playlist_item['snippet']['title']
        self.video_id = playlist_item['snippet']['resourceId']['videoId']
        self.date_published = playlist_item['snippet']['publishedAt']
        self.description = playlist_item['snippet']['description']
        self.playlist_id = playlist_item['snippet']['playlistId']   # Which playlist it's added from
        self.playlist_pos = playlist_item['snippet']['position']    # Which position it's got in the playlist

        self.url_video = YOUTUBE_URL_BASE + YOUTUBE_URL_PART_VIDEO + self.video_id
        self.url_playlist_video = self.url_video + "&list=" + self.playlist_id

        self.determine_thumbnails(playlist_item['snippet']['thumbnails'])

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
            self.thumbnails['available_quality'].append("default")      # 120x90 px
            self.thumbnails['default'] = thumbnails_item['default']
        if 'medium' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("medium")       # 320x180 px
            self.thumbnails['medium'] = thumbnails_item['medium']
        if 'high' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("high")         # 480x360 px
            self.thumbnails['high'] = thumbnails_item['high']
        if 'standard' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("standard")     # 640x480 px
            self.thumbnails['standard'] = thumbnails_item['standard']
        if 'maxres' in thumbnails_item.keys():
            self.thumbnails['available_quality'].append("maxres")       # 1280x720 px
            self.thumbnails['maxres'] = thumbnails_item['maxres']

    def set_stats(self, stats):
            self.stats_time_elapsed = stats
