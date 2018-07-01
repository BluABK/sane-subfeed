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
from collections import OrderedDict

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


def list_uploaded_videos(uploads_playlist_id, debug=False, max=25):
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube.playlistItems().list(
        maxResults=5,
        part='snippet',
        playlistId=uploads_playlist_id

    )

    print('Videos in list %s' % uploads_playlist_id)
    videos = []
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Grab information about each video.
        for playlist_item in playlistitems_list_response['items']:
            channel_title = playlist_item['snippet']['channelTitle']
            title = playlist_item['snippet']['title']
            video_id = playlist_item['snippet']['resourceId']['videoId']
            date_published = playlist_item['snippet']['publishedAt']
            description = playlist_item['snippet']['description']
            thumbnails = playlist_item['snippet']['thumbnails']

            if debug:
                print('%s\t%s%s\t%s:\t%s\t%s' % (date_published, YT_VIDEO_URL, video_id, channel_title, title,
                                                repr(description)))

            videos.append({'date': date_published, 'id': video_id, 'channel': channel_title, 'title': title,
                           'description': description, 'thumbnails': thumbnails})
            #videos.append([date_published, video_id, channel_title, title, description])
            if len(videos) >= max:
                return videos

        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)
    return videos


def get_uploads(channel_id, debug=False, max=25):
    # Get channel
    test_chan = channels_list_by_id(part='snippet,contentDetails,statistics',
                                    id=channel_id)

    # Get ID of uploads playlist
    test_chan_uploads_playlist_id = test_chan['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get playlistListResponse item of uploads playlist
    return list_uploaded_videos(test_chan_uploads_playlist_id, debug=debug, max=max)


if __name__ == '__main__':
    youtube = get_authenticated_service()

    response = subscriptions_list_my_subscriptions(client=youtube,
                                                   part='snippet,contentDetails',
                                                   mine=True)
    subscription_total = response['pageInfo']['totalResults']
    subscription_list = response['items']

    print("Found %s subscriptions." % subscription_total)

    if 'nextPageToken' in response:
        #next_page = False # FIXME: DEBUG HACK: skip processing entire sublist
        next_page = True
        next_page_token = response['nextPageToken']
        #print("DEBUG: Querying PageToken: ", end='')
        print("Querying PageTokens...")

        while next_page:
            #print(", %s" % next_page_token, end='')
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
    ocd_longest_channel_title = 0
    for item in subscription_list:
        item_id = item['id']
        channel_title = item['snippet']['title']
        channel_description = item['snippet']['description']
        channel_id = item['snippet']['resourceId']['channelId']

        # Fix spacing issues between Channel and Video Title
        if len(channel_title) > ocd_longest_channel_title:
            ocd_longest_channel_title = len(channel_title)

        subscribed_channels.update({channel_id: channel_title})

        print("[%s] %s: %s" % (channel_id, channel_title, repr(channel_description)))  # end result

    if subscription_total != len(subscription_list):
        print("WARNING: Subscription list mismatched advertised length (%s/%s)!" % (len(subscription_list),
                                                                                    subscription_total))
    new_videos_by_channel = {}
    new_videos_by_timestamp = {}
    for channel in subscription_list:
        channel_title = channel['snippet']['title']
        channel_id = channel['snippet']['resourceId']['channelId']
        print("Fetching Uploaded videos for channel: %s" % channel_title)

        new_videos_channel = get_uploads(channel_id, debug=False)

        new_videos_by_channel.update({channel_title: new_videos_channel})
        for video in new_videos_channel:
            new_videos_by_timestamp.update({video['date']: video})

    new_videos = OrderedDict(sorted(new_videos_by_timestamp.items(), reverse=True))

    # TODO: Omit really old videos from feed (possibly implement in the uploaded videos fetching part)
    # TODO: Make list havea sensible length and not subscriptions*25 (Currently mitigated by 'i')
    print("Supposedly sane and datestamp sorted subscription feed:")
    for i, (date, video) in enumerate(new_videos.items()):
        # Cut off at a sensible length # FIXME: Hack
        if i > 100:
            break
        offset = ocd_longest_channel_title - len(video['channel'])
        spacing = " " * offset + " " * 4
        print('%s\t%s%s\t%s:%s%s\t%s' % (video['date'], YT_VIDEO_URL, video['id'], video['channel'], spacing,
                                           video['title'], repr(video['description'])))

