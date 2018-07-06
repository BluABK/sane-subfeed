#!/usr/bin/python

# import argparse # TODO: Implement argparse to sanely set a lot of currently hardcoded variables.
from uploads_thread import GetUploadsThread
from math import fsum
from timeit import default_timer as timer
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


class Controller:
    youtube = None

    def __init__(self, youtube):
        self.youtube = youtube

    @staticmethod
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

    def list_subscriptions(self, client, **kwargs):
        """
        Get a list of the authenticated user's subscriptions
        :param client:
        :param kwargs:
        :return:
        """
        kwargs = self.remove_empty_kwargs(**kwargs)
        response = client.subscriptions().list(**kwargs).execute()

        return response

    def get_subscriptions(self, info=False, debug=False, traverse_pages=True):
        """
        Get a list of the authenticated user's subscriptions.
        :param info: debug lite
        :param debug:
        :param traverse_pages:
        :return: [total, subs, statistics]
        """
        _timer_start = timer()
        response = self.list_subscriptions(client=self.youtube, part='snippet,contentDetails', mine=True)
        total = response['pageInfo'][
            'totalResults']  # Advertised size of subscription list (known to be inflated reality)
        subs = response['items']  # The list of subscriptions

        _timer_end = timer()
        statistics = {'time_elapsed_page': [(_timer_end - _timer_start)]}

        if info:
            print("Found %s subscriptions." % total)

        if traverse_pages and 'nextPageToken' in response:
            next_page = True
            next_page_token = response['nextPageToken']
            # print("DEBUG: Querying PageToken: ", end='')
            if debug:
                print("Querying PageTokens...")

            while next_page:
                _timer_start = timer()
                # print(", %s" % next_page_token, end='')
                response = self.list_subscriptions(client=self.youtube, part='snippet,contentDetails',
                                                   mine=True, pageToken=next_page_token)
                subs += response['items']

                _timer_end = timer()
                statistics['time_elapsed_page'].append((_timer_end - _timer_start))

                if 'nextPageToken' in response:
                    next_page_token = response['nextPageToken']
                else:
                    print("")
                    next_page = False

        return [total, subs, statistics]

    @staticmethod
    def print_channels(subs):
        """
        Prints a list of channels and relevant data from a subscription list
        :param subs:
        :return:
        """
        for s in subs:
            print("[%s] %s: %s" % (s['snippet']['resourceId']['channelId'], s['snippet']['title'],
                                   repr(s['snippet']['description'])))

    @staticmethod
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

    @staticmethod
    def print_stats_summary(time_list, indent=''):
        """
        Print some fancy min, max and average timing stats for various code/functions.
        :param time_list:
        :param indent:
        :return:
        """
        print(indent + "Fastest load: %s seconds." % min(time_list))
        print(indent + "Slowest load: %s seconds." % max(time_list))
        print(indent + "Average load: %s seconds." % float(fsum(time_list) / float(len(time_list))))
