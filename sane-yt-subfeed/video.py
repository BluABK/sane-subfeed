class Video:
    channel_title = None
    title = None
    video_id = None
    date_published = None
    description = None
    thumbnails = {}
    playlist_id = None
    playlist_pos = None

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

        self.determine_thumbnails(playlist_item['snippet']['thumbnails'])

    def determine_thumbnails(self, thumbnails_item):
        thumbnails_item = {}    # TODO: rm -rf
        if 'default' in thumbnails_item.keys():
            self.thumbnails['available_quality'] = ["default"]
