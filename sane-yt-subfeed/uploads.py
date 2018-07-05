from authentication import youtube_auth_keys
from controller import Controller
from uploads_thread import GetUploadsThread
import time
from collections import OrderedDict
from timeit import default_timer as timer

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO


class Uploads:
    subs = None
    debug = False
    info = False
    disable_threading = False
    uploads = None
    limit = 25
    youtube = None
    load_time = 30

    def __init__(self, youtube):
        self.youtube = youtube

    def get_uploads(self, subs, debug=False, info=False, load_time=30, disable_threading=False, limit=25):
        self.subs = subs
        self.debug = debug
        self.info = info
        self.load_time = load_time
        self.disable_threading = disable_threading
        self.limit = limit
        if disable_threading:
            uploads = self.get_uploads_sequential()
        else:
            uploads = self.get_uploads_threaded()
        self.uploads = uploads
        return uploads

    def get_uploads_sequential(self):
        statistics = []
        new_videos_by_timestamp = {}

        for channel in self.subs:
            # threading.Thread()
            channel_title = channel['snippet']['title']
            channel_id = channel['snippet']['resourceId']['channelId']
            if self.info:
                print("Fetching Uploaded videos for channel: %s" % channel_title)
            tmp = self.get_channel_uploads(channel_id)
            new_videos_channel = tmp[0]
            statistics.append(tmp[1])

            for vid in new_videos_channel:
                new_videos_by_timestamp.update({vid['date']: vid})

        # Return a reverse chronological sorted OrderedDict (newest --> oldest)
        retval = OrderedDict(sorted(new_videos_by_timestamp.items(), reverse=True))
        retval['statistics'] = statistics

        return retval

    def get_uploads_threaded(self):
        """
        Returns a date-sorted OrderedDict of a list of each subscriptions' "Uploaded videos" playlist.
        :param subs: list of subscriptions
        :param debug:
        :param info: debug lite
        :param load_time: User specified expected time (in seconds) for the job to be done
        :param disable_threading: Hack to disable the currently broken threading implementation (see: Issue #1)
        :return:
        """
        statistics = []
        new_videos_by_timestamp = {}

        thread_increment = 0
        thread_list = []
        delay = self.load_time / len(self.subs)
        for channel in self.subs:
            youtube_key = youtube_auth_keys()
            uploads_new = Uploads(youtube_key)
            thread = GetUploadsThread(uploads_new, thread_increment, channel, info=True, debug=False)
            thread_list.append(thread)
            thread_increment += 1

        print("Iterating over thread list...")
        for t in thread_list:
            t.start()
            # time.sleep(delay)
            time.sleep(0.5)

        for t in thread_list:
            while t.finished() is not True:
                print("DEBUG: Thread #%s is still not done... Sleeping for 10 seconds" % t.get_id())
                time.sleep(1)
            for vid in t.get_videos():
                new_videos_by_timestamp.update({vid['date']: vid})
                statistics.append(t.get_statistics())
        retval = OrderedDict(sorted(new_videos_by_timestamp.items(), reverse=True))
        retval['statistics'] = statistics
        return retval

    def get_channel_uploads(self, channel_id):
        """
        Get a channel's "Uploaded videos" playlist, given channel ID.
        :param channel_id:
        :return: list_uploaded_videos(channel_uploads_playlist_id, debug=debug, limit=limit)
        """
        # Get channel
        channel = self.channels_list_by_id(part='snippet,contentDetails,statistics',
                                           id=channel_id)  # FIXME: stats unnecessary?

        # Get ID of uploads playlist
        channel_uploads_playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Get playlistListResponse item of uploads playlist
        return self.list_uploaded_videos(channel_uploads_playlist_id)

    def list_uploaded_videos(self, uploads_playlist_id):
        """
        Get a list of videos in a playlist
        :param uploads_playlist_id:
        :return: [list(dict): videos, dict: statistics]
        """
        _timer_start = timer()
        # Retrieve the list of videos uploaded to the authenticated user's channel.
        playlistitems_list_request = self.youtube.playlistItems().list(
            maxResults=5, part='snippet', playlistId=uploads_playlist_id)

        if self.debug:
            print('Videos in list %s' % uploads_playlist_id)

        videos = []
        channel_title = "ERROR: CHANNEL TITLE WAS N/A"  # Store the channel title for use in statistics

        while playlistitems_list_request:
            playlistitems_list_response = playlistitems_list_request.execute()

            # Grab information about each video.
            for playlist_item in playlistitems_list_response['items']: # TODO: Video obj
                channel_title = playlist_item['snippet']['channelTitle']
                title = playlist_item['snippet']['title']
                video_id = playlist_item['snippet']['resourceId']['videoId']
                date_published = playlist_item['snippet']['publishedAt']
                description = playlist_item['snippet']['description']
                thumbnails = playlist_item['snippet']['thumbnails']

                if self.debug:
                    print('%s\t%s%s\t%s:\t%s\t%s' % (date_published, YT_VIDEO_URL, video_id, channel_title, title,
                                                     repr(description)))

                videos.append({'date': date_published, 'id': video_id, 'channel': channel_title, 'title': title,
                               'description': description, 'thumbnails': thumbnails})
                # videos.append([date_published, video_id, channel_title, title, description])
                if len(videos) >= self.limit:
                    _timer_end = timer()
                    statistics = {'channel_title': channel_title, 'time_elapsed': (_timer_end - _timer_start)}
                    return [videos, statistics]

            # Keep traversing pages
            playlistitems_list_request = self.youtube.playlistItems().list_next(
                playlistitems_list_request, playlistitems_list_response)
        _timer_end = timer()
        statistics = {'channel_title': channel_title, 'time_elapsed': (_timer_end - _timer_start)}

        return [videos, statistics]

    def channels_list_by_id(self, **kwargs):
        """
        Get a youtube#channelListResponse,
        :param kwargs:
        :return: youtube#channelListResponse
        """
        kwargs = Controller.remove_empty_kwargs(**kwargs)

        response = self.youtube.channels().list(**kwargs).execute()

        return response
