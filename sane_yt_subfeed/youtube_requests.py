import json
import os
import time

from sane_yt_subfeed.authentication import youtube_auth_oauth
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.pickle_handler import dump_pickle, PICKLE_PATH, load_sub_list, load_youtube, dump_youtube, dump_sub_list
from sane_yt_subfeed.print_functions import remove_empty_kwargs
from sane_yt_subfeed.video import Video
import datetime

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO


def get_channel_uploads(youtube_key, channel_id):
    """
    Get a channel's "Uploaded videos" playlist, given channel ID.
    :param youtube_key:
    :param channel_id:
    :return: list_uploaded_videos(channel_uploads_playlist_id, debug=debug, limit=limit)
    """
    # Get channel
    channel = channels_list_by_id(youtube_key, part='snippet,contentDetails,statistics',
                                  id=channel_id)  # FIXME: stats unnecessary?

    # Get ID of uploads playlist
    channel_uploads_playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get playlistListResponse item of uploads playlist
    return list_uploaded_videos(youtube_key, channel_uploads_playlist_id)


def channels_list_by_id(youtube_key, **kwargs):
    """
    Get a youtube#channelListResponse,
    :param youtube_key:
    :param kwargs:
    :return: youtube#channelListResponse
    """
    kwargs = remove_empty_kwargs(**kwargs)

    response = youtube_key.channels().list(**kwargs).execute()

    return response


def list_uploaded_videos(youtube_key, uploads_playlist_id):
    """
    Get a list of videos in a playlist
    :param youtube_key:
    :param uploads_playlist_id:
    :return: [list(dict): videos, dict: statistics]
    """
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube_key.playlistItems().list(
        maxResults=50, part='snippet', playlistId=uploads_playlist_id)

    # TODO fix debug
    # if self.debug:
    #     print('Videos in list %s' % uploads_playlist_id)
    req_nr = 1
    req_limit = 1
    videos = []
    since_last_vid_limit = int(read_config('Requests', 'since_last_vid_limit'))
    min_diff_time = int(read_config('Requests', 'min_diff_time'))

    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for playlist_item in playlistitems_list_response['items']:
            video = Video(playlist_item)
            videos.append(video)

        if len(videos) > 0:
            max_time = videos[0].date_published
            min_time = videos[0].date_published
            for vid in videos:
                vid_date = vid.date_published
                if vid_date > max_time:
                    max_time = vid_date
                if vid_date < min_time:
                    min_time = vid_date
            time_diff = max_time - min_time
            last_vid_diff = datetime.datetime.now() - max_time
            if time_diff < datetime.timedelta(days=min_diff_time) and last_vid_diff < datetime.timedelta(
                    days=since_last_vid_limit):
                req_limit += 1

        if req_nr >= req_limit:
            # if len(videos) > 0 and videos[0].channel_title == "SYFY":
            #     print('{}: {}'.format(videos[0].channel_title, req_nr))
            #     counter = 0
            #     for v in videos:
            #         print("{}: {}".format(counter, v.title))
            #         counter += 1
                # dump_pickle(videos, os.path.join(PICKLE_PATH, 'jesse_vid_dump.pkl'))
            # if len(videos) > 0 and videos[0].channel_title == "Jesse Cox":
            #     # for vid in videos:
            #     playlistitems_list_request_2 = youtube_key.search().list(
            #         maxResults=50, part='snippet', channelId='UCCbfB3cQtkEAiKfdRQnfQvw', order='date')
            #     response = playlistitems_list_request_2.execute()
            #     for item in response['items']:
            #         print(item['snippet']['title'])
            # #   print(videos[0].thumbnails)
                # dump_pickle(videos, os.path.join(PICKLE_PATH, 'jesse_vid_dump.pkl'))
            return videos
        else:
            req_nr += 1
        playlistitems_list_request = youtube_key.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)

    return videos


def list_uploaded_videos_search(youtube_key, channel_id, search_pages):
    """
    Get a list of videos in a playlist
    :param search_pages:
    :param channel_id:
    :param youtube_key:
    :return: [list(dict): videos, dict: statistics]
    """
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube_key.search().list(
        maxResults=50, part='snippet', channelId=channel_id, order='date')

    req_limit = 1
    videos = []
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for search_result in playlistitems_list_response['items']:
            if search_result['id']['kind'] == 'youtube#video':
                video = Video(search_result)
                # print('{}: {}'.format(video.channel_title, video.title))
                # print(format(playlist_item))
                videos.append(video)

        if search_pages >= req_limit:
            return videos
        else:
            search_pages += 1

        playlistitems_list_request = youtube_key.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)

    return videos


def get_subscriptions(youtube_oauth):
    """
    Get a list of the authenticated user's subscriptions.
    :param youtube_oauth:
    :param stats:
    :param info: debug lite
    :param debug:
    :param traverse_pages:
    :return: [total, subs, statistics]
    """
    subscription_list_request = youtube_oauth.subscriptions().list(part='snippet', mine=True,
                                                                   maxResults=50)
    subs = []
    # Retrieve the list of subscribed channels for authenticated user's channel.
    while subscription_list_request:
        subscription_list_response = subscription_list_request.execute()

        # Grab information about each subscription page
        for page in subscription_list_response['items']:
            # if page['snippet']['title'] == "Jesse Cox":
            #     print('Jesse Cox: {}'.format(page['snippet']['resourceId']['channelId']))
            # print(page['snippet']['title'])
            subs.append(page)
        # print("-- Page --")
        # Keep traversing pages # FIXME: Add limitation
        subscription_list_request = youtube_oauth.playlistItems().list_next(
            subscription_list_request, subscription_list_response)

    return subs


def cached_authenticated_get_subscriptions():
    cached_subs = read_config('Debug', 'cached_subs')
    if cached_subs:
        try:
            temp_subscriptions = load_sub_list()
        except FileNotFoundError:
            try:
                youtube_oauth = load_youtube()
            except FileNotFoundError:
                youtube_oauth = youtube_auth_oauth()
                dump_youtube(youtube_oauth)
            temp_subscriptions = get_subscriptions(youtube_oauth)
            dump_sub_list(temp_subscriptions)
    else:
        try:
            youtube_oauth = load_youtube()
            temp_subscriptions = get_subscriptions(youtube_oauth)
        except FileNotFoundError:
            youtube_oauth = youtube_auth_oauth()
            dump_youtube(youtube_oauth)
            temp_subscriptions = get_subscriptions(youtube_oauth)
    return temp_subscriptions
