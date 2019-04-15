#!/usr/bin/python

# import argparse # TODO: Implement argparse to sanely set a lot of currently hardcoded variables.
from math import fsum
# Google/YouTube API
# import google.oauth2.credentials
# import google_auth_oauthlib.flow

# from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets


# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.


YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YOUTUBE_PARM_PLIST = "playlist?list ="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO
VIDEO_FILTER_DOWNLOADED = 0
VIDEO_FILTER_WATCHED = 1
VIDEO_FILTER_DISCARDED = 2


def remove_empty_kwargs(**kwargs):
    """
    Remove keyword arguments that are not set.
    :param kwargs:
    :return:
    """
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value

    return good_kwargs


def print_channels(subs):
    """
    Prints a list of channels and relevant data from a subscription list
    :param subs:
    :return:
    """
    for s in subs:
        print("[%s] %s: %s" % (s['snippet']['resourceId']['channelId'], s['snippet']['title'],
                               repr(s['snippet']['description'])))


def print_subscription_feed(subfeed, cutoff=20):
    """
    Print a basic listing of the processed subscription feed.
    :param subfeed:
    :param cutoff: How many videos/items to list
    :return:
    """

    # Loop through subfeed and determine the longest channel name (for OCD/indent purposes) # TODO: Generalise
    longest_title = 0
    counter = 0
    for video in subfeed:
        if len(video.channel_title) > longest_title:
            longest_title = len(video.channel_title)
        counter += 1
        if counter > cutoff:
            break

    # TODO: Omit really old videos from feed (possibly implement in the uploaded videos fetching part)
    # TODO: Make list have a sensible length and not subscriptions*25 (Currently mitigated by 'i')
    counter = 0
    for video in subfeed:
        # Cut off at a sensible length # FIXME: Hack
        if counter > cutoff:
            break
        # TODO: Use longest title of current list, not entire subscriptions.
        offset = longest_title - len(video.channel_title)
        spacing = " " * offset + " " * 4
        print('%s\t%s%s\t%s:%s%s\t%s…' % (video.date_published, YT_VIDEO_URL, video.video_id, video.channel_title,
                                          spacing, video.title, repr(video.description)[0:30]))
        counter += 1


def remove_duplicates(list_with_dupes: list):
    """
    Removes duplicate entries in a list by passing it through a set.
    :param list_with_dupes:
    :return:
    """
    return list(set(list_with_dupes))


def remove_duplicate_videos(list_with_dupes: list):
    """
    Removes duplicate entries in a list by filtering them by video_id.
    :param list_with_dupes:
    :return:
    """
    video_ids = set()
    videos_deduped = []
    for video in list_with_dupes:
        if video.video_id not in video_ids:
            videos_deduped.append(video)
            video_ids.add(video.video_id)

    return videos_deduped


def print_videos(videos, path_only=False, allow_duplicates=True):
    """
    Prints a list of videos to stdout.
    :param allow_duplicates:
    :param path_only: print only vid_path attribute
    :param videos: a list of Video objects.
    :return:
    """
    if not allow_duplicates:
        videos = remove_duplicate_videos(videos)

    for video in videos:
        if path_only:
            # Only print entries that have a video path
            if video.vid_path:
                print("{}".format(video.vid_path))
        else:
            print("{}".format(video))


def print_videos_filtered(videos, video_filter, path_only=False):
    """
    Prints filtered a list of videos to stdout.
    :param path_only: print only vid_path attribute
    :param videos: a list of Video objects.
    :param video_filter: Print videos matching this criteria.
    :return:
    """
    for video in videos:
        if video_filter:
            if video_filter == VIDEO_FILTER_DOWNLOADED and video.downloaded:
                if path_only:
                    print("{}".format(video.vid_path))
                else:
                    print("{}".format(video))
            if video_filter == VIDEO_FILTER_DISCARDED and video.discarded:
                if path_only:
                    print("{}".format(video.vid_path))
                else:
                    print("{}".format(video))
            if video_filter == VIDEO_FILTER_WATCHED and video.watched:
                if path_only:
                    print("{}".format(video.vid_path))
                else:
                    print("{}".format(video))
        else:
            # If no filter, print all videos in DB
            print("{}".format(video.vid_path))


