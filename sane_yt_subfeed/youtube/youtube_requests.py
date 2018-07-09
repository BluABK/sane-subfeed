from sane_yt_subfeed.authentication import youtube_auth_oauth
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.pickle_handler import load_sub_list, load_youtube, dump_youtube, dump_sub_list
from sane_yt_subfeed.print_functions import remove_empty_kwargs
from sane_yt_subfeed.database.video import Video
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
    channel = channels_list_by_id(youtube_key, part='contentDetails',
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

            return
        else:
            req_nr += 1
        playlistitems_list_request = youtube_key.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)

    return


def list_uploaded_videos_search(youtube_key, channel_id, videos, search_pages):
    """
    Get a list of videos through the API search()
    Quota cost: 100 units / response
    :param videos:
    :param search_pages:
    :param channel_id:
    :param youtube_key:
    :return: [list(dict): videos, dict: statistics]
    """
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube_key.search().list(
        maxResults=50, part='snippet', channelId=channel_id, order='date')
    req_limit = 1
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for search_result in playlistitems_list_response['items']:
            if search_result['id']['kind'] == 'youtube#video':
                videos.append(VideoD(search_result))
        if search_pages >= req_limit:
            break
        else:
            search_pages += 1

        playlistitems_list_request = youtube_key.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)
    db_session.commit()


def get_remote_subscriptions(youtube_oauth):
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
            channel = Channel(page['snippet'])
            db_video = db_session.query(Channel).get(channel.id)
            if db_video:
                # TODO update object
                subs.append(channel)
            else:
                db_session.add(channel)
                subs.append(channel)
        # print("-- Page --")
        # Keep traversing pages # FIXME: Add limitation
        subscription_list_request = youtube_oauth.playlistItems().list_next(
            subscription_list_request, subscription_list_response)
    db_session.commit()
    return subs


def get_subscriptions(cached_subs):
    if cached_subs:
        return get_stored_subscriptions()
    else:
        return get_remote_subscriptions_cached_oauth()


def get_stored_subscriptions():
    channels = db_session.query(Channel).all()
    if len(channels) < 1:
        return get_remote_subscriptions_cached_oauth()
    return channels


def get_remote_subscriptions_cached_oauth():
    try:
        youtube_oauth = load_youtube()
        temp_subscriptions = get_remote_subscriptions(youtube_oauth)
    except FileNotFoundError:
        youtube_oauth = youtube_auth_oauth()
        dump_youtube(youtube_oauth)
        temp_subscriptions = get_remote_subscriptions(youtube_oauth)
    return temp_subscriptions
