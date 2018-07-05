from authentication import youtube_auth_keys
from controller import Controller
from uploads_thread import GetUploadsThread
from video import Video
import time
from collections import OrderedDict
from timeit import default_timer as timer
from tqdm import tqdm # fancy progress bar

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

            for video in new_videos_channel:
                new_videos_by_timestamp.update({video.date_published: video})

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

        print("Creating YouTube service object from API_KEY for %s channels:" % len(self.subs))
        for channel in tqdm(self.subs):
            if self.debug:
                print("Creating YouTube service object from API_KEY for channel: %s" % channel['snippet']['title'])
            youtube_key = youtube_auth_keys()
            uploads_new = Uploads(youtube_key)
            thread = GetUploadsThread(uploads_new, thread_increment, channel, info=True, debug=False)
            thread_list.append(thread)
            thread_increment += 1

        print("\nStarting threads:")
        for t in tqdm(thread_list):
            t.start()
            # time.sleep(delay)
            time.sleep(0.010)

        print("\nCollecting data from %s threads:" % len(thread_list))
        for t in tqdm(thread_list):
            while t.finished() is not True:
                if self.debug:
                    print("\nNOTE: Thread #%s is still not done... Sleeping for 0.010 seconds" % t.get_id())
                time.sleep(0.010)
            for vid in t.get_videos():
                new_videos_by_timestamp.update({vid.date_published: vid})
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
            first_run = True
            for playlist_item in playlistitems_list_response['items']:
                video = Video(playlist_item)

                if first_run:
                    channel_title = video.channel_title  # Used for statistics

                if self.debug:
                    print('%s\t%s%s\t%s:\t%s\t%s' % (video.date_published, YT_VIDEO_URL, video.video_id,
                                                     video.channel_title, video.title, repr(video.description)))
                # TODO: clean
                #videos.append({'date': video.date_published, 'id': video.video_id, 'channel': video.channel_title, 'title': video.title,
                #               'description': video.description, 'thumbnails': video.thumbnails})
                videos.append(video)
                if len(videos) >= self.limit:
                    _timer_end = timer()    # end timer for channel statistics (*NOT* video)
                    statistics = {'channel_title': video.channel_title, 'time_elapsed': (_timer_end - _timer_start)}
                    return [videos, statistics]     # TODO: Make channel stats into object and give ptr to Video?

            # Keep traversing pages # FIXME: Add limitation
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
