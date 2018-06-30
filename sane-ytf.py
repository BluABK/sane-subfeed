#!/usr/bin/python

# Retrieve the authenticated user's uploaded videos.
# Sample usage:
# python my_uploads.py

import argparse
import os
import re

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# Internal resources
# import my_uploads

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
CLIENT_SECRETS_FILE = 'client_secret.json'

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

YOUTUBE_URL = "https://www.youtube.com/"
YOUTUBE_PARM_VIDEO = "watch?v="
YT_VIDEO_URL = YOUTUBE_URL + YOUTUBE_PARM_VIDEO


# Authorize the request and store authorization credentials.
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


# Remove keyword arguments that are not set.
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value

    return good_kwargs


def subscriptions_list_my_subscriptions(client, **kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.subscriptions().list(
        **kwargs
    ).execute()

    # return print_response(response)
    return response


def channels_list_by_id(**kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = youtube.channels().list(
        **kwargs
    ).execute()

    return response


def playlists_list_by_id(**kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = youtube.playlists().list(**kwargs).execute()

    return response


def playlist_items_list_by_playlist_id(**kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = youtube.playlistItems().list(**kwargs).execute()

    return response


def list_uploaded_videos(uploads_playlist_id):
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part='snippet',
        maxResults=5
    )

    print('Videos in list %s' % uploads_playlist_id)
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Print information about each video.
        for playlist_item in playlistitems_list_response['items']:
            title = playlist_item['snippet']['title']
            video_id = playlist_item['snippet']['resourceId']['videoId']
            date_published = playlist_item['snippet']['publishedAt']
            description = playlist_item['snippet']['description']
            thumbnails = playlist_item['snippet']['thumbnails']

            print('%s\t%s%s\t%s\t%s' % (date_published, YT_VIDEO_URL, video_id, title, repr(description)))

        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)


if __name__ == '__main__':
    youtube = get_authenticated_service()

    # Get channel
    test_chan = channels_list_by_id(part='snippet,contentDetails,statistics',
                                    id='UCZn2JQsQd3MXH07aI9TDI3g')

    # Get ID of uploads playlist
    test_chan_uploads_playlist_id = test_chan['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get playlistListResponse item of uploads playlist
    list_uploaded_videos(test_chan_uploads_playlist_id)

    exit()
    response = subscriptions_list_my_subscriptions(client=youtube,
                                                   part='snippet,contentDetails',
                                                   mine=True)
    subscription_total = response['pageInfo']['totalResults']
    subscription_list = response['items']

    print("Found %s subscriptions." % subscription_total)

    if 'nextPageToken' in response:
        next_page = True
        next_page_token = response['nextPageToken']
        print("DEBUG: Querying PageToken: ", end='')

        while next_page:
            print(", %s" % next_page_token, end='')
            this_response = subscriptions_list_my_subscriptions(client=youtube,
                                                                part='snippet,contentDetails',
                                                                mine=True,
                                                                pageToken=next_page_token)
            subscription_list += this_response['items']

            if 'nextPageToken' in this_response:
                next_page_token = this_response['nextPageToken']
            else:
                print("")
                next_page = False

    subscribed_channels = {}
    for item in subscription_list:
        item_id = item['id']
        channel_title = item['snippet']['title']
        channel_description = item['snippet']['description']
        channel_id = item['snippet']['resourceId']['channelId']

        subscribed_channels.update({channel_id: channel_title})

        print("[%s] %s: %s" % (channel_id, channel_title, repr(channel_description)))  # end result

    if subscription_total != len(subscription_list):
        print("WARNING: Subscription list mismatched advertised length (%s/%s)!" % (len(subscription_list),
                                                                                    subscription_total))

    print("================ DEBUG SPAM COMMENCES BELOW THIS LINE ================")
    print(subscription_list)
