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
    for i, (date, video) in enumerate(subfeed.items()):
        if len(video.channel_title) > longest_title:
            longest_title = len(video.channel_title)
        if i > cutoff:
            break

    # TODO: Omit really old videos from feed (possibly implement in the uploaded videos fetching part)
    # TODO: Make list have a sensible length and not subscriptions*25 (Currently mitigated by 'i')
    for i, (date, video) in enumerate(subfeed.items()):
        # Cut off at a sensible length # FIXME: Hack
        if i > cutoff:
            break
        # TODO: Use longest title of current list, not entire subscriptions.
        offset = longest_title - len(video.channel_title)
        spacing = " " * offset + " " * 4

        print('%s\t%s%s\t%s:%s%s\t%s…' % (video.date_published, YT_VIDEO_URL, video.video_id, video.channel_title,
                                          spacing, video.title, repr(video.description)[0:30]))