import time

from googleapiclient.errors import HttpError
from sqlalchemy import or_
from tqdm import tqdm

from sane_yt_subfeed.authentication import youtube_auth_oauth
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.detached_models.video_d import VideoD, GRAB_METHOD_SEARCH, GRAB_METHOD_LIST, \
    GRAB_METHOD_VIDEOS
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.orm import db_session, engine
from sane_yt_subfeed.database.write_operations import engine_execute_first, engine_execute, delete_sub_not_in_list
from sane_yt_subfeed.database.engine_statements import update_channel_from_remote, get_channel_by_id_stmt
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.pickle_handler import load_sub_list, load_youtube, dump_youtube, dump_sub_list
from sane_yt_subfeed.print_functions import remove_empty_kwargs
import datetime

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)

# FIXME: integrate with socket system
logger_list_search = create_logger("youtube_requests: list()/search()", logfile="debug_list_search.log")


def get_channel_uploads_playlist_id(youtube_key, channel_id):
    """
    Get a channel's "Uploaded videos" playlist ID, given channel ID.
    :param youtube_key:
    :param channel_id:
    :return: list_uploaded_videos(channel_uploads_playlist_id, debug=debug, limit=limit)
    """
    # Get channel
    channel = channels_list_by_id(youtube_key, part='contentDetails',
                                  id=channel_id)  # FIXME: stats unnecessary?

    # Get ID of uploads playlist
    # TODO: store channel_id in channel, making one less extra request
    return channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']


def get_channel(youtube_key, channel_id):
    """
    Get a channel response, given its ID.
    :param youtube_key:
    :param channel_id:
    :return: A channelList response
    """
    # Get channel
    channel = channels_list_by_id(youtube_key, part='contentDetails,snippet',
                                  id=channel_id)  # FIXME: stats unnecessary?

    # Get ID of uploads playlist
    # TODO: store channel_id in channel, making one less extra request
    return channel['items'][0]  # Send full response since id is outside of snippet


def get_channel_uploads(youtube_key, channel_id, videos, req_limit):
    """
    Get a channel's "Uploaded videos" playlist, given channel ID.
    Carries videos and req_limit for use outside this scope.
    :param req_limit: carried from outside scope
    :param videos: carried from outside scope
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
            if read_config('Debug', 'log_list') and read_config('Debug', 'log_needle') != 'unset':
                if search_result['snippet']['channelTitle'] == str(read_config('Debug', 'log_needle')):
                    logger_list_search.debug("list():\t {} ({}) - {} | Desc: {}".format(search_result['snippet']['channelTitle'],
                                                                             search_result['snippet']['publishedAt'],
                                                                             search_result['snippet']['title'],
                                                                             search_result['snippet']['description']))

            if read_config('Debug', 'log_list') and read_config('Debug', 'log_needle') == 'unset':
                logger_list_search.debug("list():\t {} ({}) - {}".format(search_result['snippet']['channelTitle'],
                                                                         search_result['snippet']['publishedAt'],
                                                                         search_result['snippet']['title']))

            videos.append(VideoD.playlist_item_new_video_d(search_result, grab_methods=[GRAB_METHOD_LIST]))
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


def list_uploaded_videos_videos(youtube_key, video_ids, req_limit, part='snippet'):
    """
    Get a list of videos through the API videos()
    Quota cost: 2-3 units / part / request
    :param part:
    :param video_ids: a list of ids to request video from
    :param req_limit:
    :param youtube_key:
    :return: [list(dict): videos, dict: statistics]
    """
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    videos = []
    string_video_ids = ','.join(map(str, video_ids))

    playlistitems_list_request = youtube_key.videos().list(
        maxResults=50, part=part, id=string_video_ids)
    search_pages = 0
    while playlistitems_list_request:
        search_pages += 1
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for search_result in playlistitems_list_response['items']:
            videos.append(VideoD.videos_item_new_video_d(search_result, grab_methods=[GRAB_METHOD_VIDEOS]))
        if search_pages >= req_limit:
            break
        playlistitems_list_request = youtube_key.playlistItems().list_next(playlistitems_list_request,
                                                                           playlistitems_list_response)
    return videos


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
                if read_config('Debug', 'log_search') and read_config('Debug', 'log_needle') != 'unset':
                    if search_result['snippet']['channelTitle'] == str(read_config('Debug', 'log_needle')):
                        title = search_result['snippet']['title']
                        if search_result['snippet']['liveBroadcastContent'] != "none":
                            title += " [LIVESTREAM]"
                            logger_list_search.debug(
                                "search():\t {} ({}) - {} | Desc: {}".format(search_result['snippet']['channelTitle'],
                                                                  search_result['snippet']['publishedAt'], title,
                                                                             search_result['snippet']['description']))

                if read_config('Debug', 'log_search') and read_config('Debug', 'log_needle') == 'unset':
                    title = search_result['snippet']['title']
                    if search_result['snippet']['liveBroadcastContent'] != "none":
                        title += " [LIVESTREAM]"
                        logger_list_search.debug(
                            "search():\t {} ({}) - {}".format(search_result['snippet']['channelTitle'],
                                                              search_result['snippet']['publishedAt'], title))

                videos.append(VideoD(search_result, grab_methods=[GRAB_METHOD_SEARCH]))
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
    channel_ids = []
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
                create_logger(__name__ + ".subscriptions").info(
                    "Added channel {} - {}".format(channel.title, channel.id))
                db_session.add(channel)
                subs.append(channel)
            channel_ids.append(channel.id)
        subscription_list_request = youtube_oauth.playlistItems().list_next(
            subscription_list_request, subscription_list_response)
    delete_sub_not_in_list(channel_ids)
    db_session.commit()
    return subs


def get_subscriptions(cached_subs):
    if cached_subs:
        return get_stored_subscriptions()
    else:
        return get_remote_subscriptions_cached_oauth()


def get_stored_subscriptions():
    logger.info("Getting subscriptions from DB.")
    channels = db_session.query(Channel).filter(or_(Channel.subscribed, Channel.subscribed_override)).all()
    if len(channels) < 1:
        return get_remote_subscriptions_cached_oauth()
    return channels


def get_remote_subscriptions_cached_oauth():
    logger.info("Getting subscriptions from remote (cached OAuth).")
    try:
        youtube_oauth = load_youtube()
        temp_subscriptions = get_remote_subscriptions(youtube_oauth)
    except FileNotFoundError:
        logger.warning("Loading of cached OAuth: File not found. Requesting new OAuth from user.")
        youtube_oauth = youtube_auth_oauth()
        dump_youtube(youtube_oauth)
        temp_subscriptions = get_remote_subscriptions(youtube_oauth)
    return temp_subscriptions


def add_subscription_remote(channel_id):
    """
    Add a YouTube subscription (On YouTube).

    DEPRECATED: Google doesn't let you, see supported op table https://developers.google.com/youtube/v3/getting-started
    :param youtube_oauth:
    :param channel_id:
    :return: returns response or raises exception
    """
    youtube_oauth = load_youtube()
    response = youtube_oauth.subscriptions().insert(
        part='snippet',
        body=dict(
            snippet=dict(
                resourceId=dict(
                    channelId=channel_id
                )
            )
        )
    )
    try:
        response.execute()
    except HttpError as exc_http:
        _msg = "Failed adding subscription to '{}', HTTP Error {}".format(channel_id, exc_http.resp.status)
        logger.error("{}: {}".format(_msg, exc_http.content), exc_info=exc_http)
        raise exc_http

    except Exception as exc:
        _msg = "Unhandled exception occurred when adding subscription to '{}'".format(channel_id)
        logger.critical("{} | response={}".format(_msg, response.__dict__), exc_info=exc)
        raise exc

    # FIXME: Somewhat duplicate code of get_remote_subscriptions, move to own function -- START
    # Get ID of uploads playlist
    channel_uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    channel = Channel(channel_id, channel_uploads_playlist_id)
    db_channel = engine_execute_first(get_channel_by_id_stmt(channel))
    if db_channel:
        engine_execute(update_channel_from_remote(channel))
        # subs.append(channel)
    else:
        # TODO: change to sqlalchemy core stmt
        create_logger(__name__ + ".subscriptions").info(
            "Added channel {} - {}".format(channel.title, channel.id))
        db_session.add(channel)
        # subs.append(channel)

    db_session.commit()
    # FIXME: Somewhat duplicate code of get_remote_subscriptions, move to own function -- END

    logger.info("Added subscription: {} / {}".format(channel_id, response['snippet']['title']))
    return response


def add_subscription_local(youtube_auth, channel_id):
    """
    Add a YouTube subscription (Local/DB).
    :param youtube_auth:
    :param channel_id:
    :return:
    """
    # FIXME: Somewhat duplicate code of get_remote_subscriptions, move to own function -- START
    # Get ID of uploads playlist
    # channel_uploads_playlist_id = get_channel_uploads_playlist_id(youtube_auth, channel_id)
    channel_response = get_channel(youtube_auth, channel_id)
    channel_uploads_playlist_id = channel_response['contentDetails']['relatedPlaylists']['uploads']
    channel = Channel(channel_response, channel_uploads_playlist_id, channel_list_response=True)
    db_channel = engine_execute_first(get_channel_by_id_stmt(channel))
    if db_channel:
        engine_execute(update_channel_from_remote(channel))
    else:
        # TODO: change to sqlalchemy core stmt
        create_logger(__name__ + ".subscriptions").info(
            "Added channel {} - {}".format(channel.title, channel.id))
        db_session.add(channel)

    db_session.commit()
    # FIXME: Somewhat duplicate code of get_remote_subscriptions, move to own function -- END

    logger.info("Added subscription (Local/DB): {} / {}".format(channel_id, channel.title))


def add_subscription(youtube_auth, channel_id):
    """
    Add a YouTube Channel subscription.
    :param youtube_auth: api key or oauth
    :param channel_id:
    :return: returns response or raises exception
    """
    add_subscription_local(youtube_auth, channel_id)
    # add_subscription_remote(channel_id) # DEPRECATED, see its docstring
