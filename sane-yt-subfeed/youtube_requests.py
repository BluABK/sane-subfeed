from print_functions import remove_empty_kwargs
from video import Video

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

    videos = []
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for playlist_item in playlistitems_list_response['items']:
            video = Video(playlist_item)

            # TODO fix debug
            # if self.debug:
            #print('%s\t%s%s\t%s:\t%s\t%s' % (video.date_published, YT_VIDEO_URL, video.video_id,
            #                                 video.channel_title, video.title, repr(video.description)))
            videos.append(video)
            # TODO fix debug
            if len(videos) >= 25:
                return videos

        # Keep traversing pages # FIXME: Add limitation
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
    subscription_list_request = youtube_oauth.subscriptions().list(part='snippet,contentDetails', mine=True,
                                                                   maxResults=50)
    subs = []
    # Retrieve the list of subscribed channels for authenticated user's channel.
    while subscription_list_request:
        subscription_list_response = subscription_list_request.execute()

        # Grab information about each subscription page
        for page in subscription_list_response['items']:
            #print(page['snippet']['title'])
            subs.append(page)
        #print("-- Page --")
        # Keep traversing pages # FIXME: Add limitation
        subscription_list_request = youtube_oauth.playlistItems().list_next(
            subscription_list_request, subscription_list_response)

    return subs

