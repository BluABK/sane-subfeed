import time

from tqdm import tqdm

from sane_yt_subfeed.authentication import youtube_auth_oauth
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.orm import db_session, engine
from sane_yt_subfeed.database.write_operations import engine_execute_first, engine_execute
from sane_yt_subfeed.database.engine_statements import update_channel_from_remote, get_channel_by_id_stmt
from sane_yt_subfeed.log_handler import logger
from sane_yt_subfeed.pickle_handler import load_sub_list, load_youtube, dump_youtube, dump_sub_list
from sane_yt_subfeed.print_functions import remove_empty_kwargs
import datetime

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO


def get_channel_uploads(youtube_key, channel_id, videos, req_limit):
    """
    Get a channel's "Uploaded videos" playlist, given channel ID.
    :param req_limit:
    :param videos:
    :param youtube_key:
    :param channel_id:
    :return: list_uploaded_videos(channel_uploads_playlist_id, debug=debug, limit=limit)
    """
    # Get channel
    channel = channels_list_by_id(youtube_key, part='contentDetails',
                                  id=channel_id)  # FIXME: stats unnecessary?

    # Get ID of uploads playlist
    # TODO: store channel_id in channel, making one less extra request
    channel_uploads_playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get playlistListResponse item of uploads playlist
    return list_uploaded_videos(youtube_key, videos, req_limit, channel_uploads_playlist_id)


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


def list_uploaded_videos(youtube_key, videos, uploads_playlist_id, req_limit):
    """
    Get a list of videos in a playlist
    :param req_limit:
    :param videos:
    :param youtube_key:
    :param uploads_playlist_id:
    :return: [list(dict): videos, dict: statistics]
    """
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube_key.playlistItems().list(
        maxResults=50, part='snippet', playlistId=uploads_playlist_id)

    searched_pages = 0
    while playlistitems_list_request:
        searched_pages += 1
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for search_result in playlistitems_list_response['items']:
            if read_config('Debug', 'log_list'):
                logger.debug("list():\t {} ({}) - {}".format(search_result['snippet']['channelTitle'],
                                                             search_result['snippet']['publishedAt'],
                                                             search_result['snippet']['title']))
            videos.append(VideoD.playlist_item_new_video_d(search_result))
        if searched_pages >= req_limit:
            break

        playlistitems_list_request = youtube_key.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)


def list_uploaded_videos_page(youtube_key, videos, uploads_playlist_id, playlistitems_list_request=None):
    if not playlistitems_list_request:
        playlistitems_list_request = youtube_key.playlistItems().list(
            maxResults=50, part='snippet', playlistId=uploads_playlist_id)

    playlistitems_list_response = playlistitems_list_request.execute()

    # Grab information about each video.
    for search_result in playlistitems_list_response['items']:
        videos.append(VideoD.playlist_item_new_video_d(search_result))

    return youtube_key.playlistItems().list_next(
        playlistitems_list_request, playlistitems_list_response)


def list_uploaded_videos_search(youtube_key, channel_id, videos, req_limit, live_videos=True):
    """
    Get a list of videos through the API search()
    Quota cost: 100 units / response
    :param live_videos:
    :param videos:
    :param req_limit:
    :param channel_id:
    :param youtube_key:
    :return: [list(dict): videos, dict: statistics]
    """
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube_key.search().list(
        maxResults=50, part='snippet', channelId=channel_id, order='date')
    search_pages = 0
    while playlistitems_list_request:
        search_pages += 1
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for search_result in playlistitems_list_response['items']:
            live_broadcast_snippet = search_result['snippet']['liveBroadcastContent']
            live_broadcast = live_broadcast_snippet == 'none'
            if (not live_videos) and (not live_broadcast):
                break
            if search_result['id']['kind'] == 'youtube#video':
                if read_config('Debug', 'log_search'):
                    title = search_result['snippet']['title']
                    if search_result['snippet']['liveBroadcastContent'] != "none":
                        title += " [LIVESTREAM]"
                    logger.debug("search():\t {} ({}) - {}".format(search_result['snippet']['channelTitle'],
                                                                   search_result['snippet']['publishedAt'], title))
                videos.append(VideoD(search_result))
        if search_pages >= req_limit:
            break

        playlistitems_list_request = youtube_key.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)


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
    update_stmts = []
    while subscription_list_request:
        subscription_list_response = subscription_list_request.execute()

        # Grab information about each subscription page
        for page in tqdm(subscription_list_response['items'], desc="Adding and updating channels by page",
                         disable=read_config('Debug', 'disable_tqdm')):
            # Get channel
            channel_response = channels_list_by_id(youtube_oauth, part='contentDetails',
                                                   id=page['snippet']['resourceId']['channelId'])

            # Get ID of uploads playlist
            channel_uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            channel = Channel(page['snippet'], channel_uploads_playlist_id)
            db_channel = engine_execute_first(get_channel_by_id_stmt(channel))
            if db_channel:
                engine_execute(update_channel_from_remote(channel))
                subs.append(channel)
            else:
                # TODO: change to sqlalchemy core stmt
                db_session.add(channel)
                subs.append(channel)
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
