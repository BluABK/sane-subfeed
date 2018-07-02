#!/usr/bin/python

# Retrieve the authenticated user's uploaded videos.
# Sample usage:
# python my_uploads.py

# import argparse
from math import fsum
from collections import OrderedDict
from timeit import default_timer as timer
import time
import threading
# import multiprocessing.dummy as mp

# Google/YouTube API
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
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


def list_subscriptions(client, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.subscriptions().list(**kwargs).execute()

    return response


def channels_list_by_id(**kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = youtube.channels().list(**kwargs).execute()

    return response


def list_uploaded_videos(uploads_playlist_id, debug=False, limit=25):
    _timer_start = timer()
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube.playlistItems().list(
        maxResults=5, part='snippet', playlistId=uploads_playlist_id)

    if debug:
        print('Videos in list %s' % uploads_playlist_id)

    videos = []
    channel_title = "ERROR: CHANNEL TITLE WAS N/A"  # Store the channel title for use in statistics
    plist_url_base = "https://www.youtube.com/playlist?list="
    while playlistitems_list_request:
        successful = False
        attempts = 0
        # Handle bad requests (SSLEror etc)
        while not successful or attempts > 5:
            try:
                playlistitems_list_response = playlistitems_list_request.execute()
                successful = True
            except SystemExit as e:
                attempts += 1
                print("list_uploaded_videos(%s%s) [Exception] SystemExit: %s (attempt: %s )" % (plist_url_base,
                                                                                                uploads_playlist_id,
                                                                                                e, attempts))
                pass
            except Exception as e:
                attempts += 1
                print("list_uploaded_videos(%s%s) [Exception] Exception: %s (attempt: %s )" % (plist_url_base,
                                                                                               uploads_playlist_id,
                                                                                               e, attempts))
                pass
        if attempts > 5:
            print("list_uploaded_videos(%s%s): Failed all 5 attempts" % (plist_url_base, uploads_playlist_id))

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
            # videos.append([date_published, video_id, channel_title, title, description])
            if len(videos) >= limit:
                _timer_end = timer()
                statistics = {'channel_title': channel_title, 'time_elapsed': (_timer_end - _timer_start)}
                return [videos, statistics]

        # Keep traversing pages
        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)
    _timer_end = timer()
    statistics = {'channel_title': channel_title, 'time_elapsed': (_timer_end - _timer_start)}

    return [videos, statistics]


def get_uploads(channel_id, debug=False, limit=25):
    successful = False
    attempts = 0
    # Handle bad requests (SSLEror etc)
    while not successful or attempts > 5:
        try:
            # Get channel
            channel = channels_list_by_id(part='snippet,contentDetails,statistics', id=channel_id)

            successful = True
        except SystemExit as e:
            attempts += 1
            print("get_uploads(%s): [Exception] SystemExit: %s (attempt: %s)" % (channel_id, e, attempts))
            pass
        except Exception as e:
            attempts += 1
            print("get_uploads(%s): [Exception] Exception: %s (attempt: %s )" % (channel_id, e, attempts))
            pass
    if attempts > 5:
        print("get_uploads(%s): Failed all 5 attempts." % channel_id)
        return "get_uploads(%s): Failed all 5 attempts." % channel_id

    # Get ID of uploads playlist
    channel_uploads_playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get playlistListResponse item of uploads playlist
    return list_uploaded_videos(channel_uploads_playlist_id, debug=debug, limit=limit)


def get_subscriptions(info=False, debug=False, traverse_pages=True):
    _timer_start = timer()
    response = list_subscriptions(client=youtube, part='snippet,contentDetails', mine=True)
    total = response['pageInfo']['totalResults']
    subs = response['items']

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
            response = list_subscriptions(client=youtube, part='snippet,contentDetails',
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


def process_subscriptions(subs, info=False):
    channels = {}
    longest_title = 0

    for _item in subs:
        title = _item['snippet']['title']
        description = _item['snippet']['description']
        cid = _item['snippet']['resourceId']['channelId']

        # Fix spacing issues between Channel and Video Title
        if len(title) > longest_title:
            longest_title = len(title)

        # Put channels and relevant data into a dict that is easier to handle
        channels.update({'id': cid, 'title': title, 'description': description, 'longest_title': longest_title})

        if info:
            print("[%s] %s: %s" % (id, title, repr(description)))

    return channels


class GetUploadsThread(threading.Thread):
    def __init__(self, thread_id, channel, info=False, debug=False):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.channel = channel
        self.info = info
        self.debug = debug
        self.statistics = {}
        self.videos = []
        self.job_done = False

    # TODO: Handle failed requests
    def run(self):
        channel_title = self.channel['snippet']['title']
        channel_id = self.channel['snippet']['resourceId']['channelId']
        print("Starting #%s for channel: %s" % (self.thread_id, channel_title), end='')
        if self.info:
            print(" -- Fetching Uploaded videos for channel: %s" % channel_title)
        else:
            print("")
        retval = get_uploads(channel_id, debug=self.debug)

        self.videos = retval[0]
        self.statistics = retval[1]

        self.job_done = True
        print("Exiting #%s" % self.thread_id)

    def get_videos(self):
        return self.videos

    def get_statistics(self):
        return self.statistics

    def get_id(self):
        return self.thread_id

    def finished(self):
        return self.job_done


def get_uploads_all_channels(subs, debug=False, info=False, load_time=30, disable_threading=False):
    statistics = []
    new_videos_by_timestamp = {}

    thread_increment = 0
    thread_list = []
    delay = load_time/len(subs)
    if not disable_threading:
        for channel in subs:
            thread = GetUploadsThread(thread_increment, channel, info=True, debug=False)
            thread_list.append(thread)
            thread_increment += 1

        print("Iterating over thread list...")
        for t in thread_list:
            t.start()
            #time.sleep(delay)
            time.sleep(1)

        for t in thread_list:
            while t.finished() is not True:
                print("DEBUG: Thread #%s is still not done... Sleeping for 10 seconds" % t.get_id())
                time.sleep(1)
            for vid in t.get_videos():
                new_videos_by_timestamp.update({vid['date']: vid})
                statistics.append(t.get_statistics())

    # TODO: Legacy failsafe until thread implementation works
    else:
        for channel in subs:
            # threading.Thread()
            channel_title = channel['snippet']['title']
            channel_id = channel['snippet']['resourceId']['channelId']
            if info:
                print("Fetching Uploaded videos for channel: %s" % channel_title)
            tmp = get_uploads(channel_id, debug=debug)
            new_videos_channel = tmp[0]
            statistics.append(tmp[1])

            for vid in new_videos_channel:
                new_videos_by_timestamp.update({vid['date']: vid})

    # Return a reverse chronological sorted OrderedDict (newest --> oldest)
    retval = OrderedDict(sorted(new_videos_by_timestamp.items(), reverse=True))
    retval['statistics'] = statistics

    return retval


def print_subscription_feed(subfeed, longest_title, cutoff=20):
    # TODO: Omit really old videos from feed (possibly implement in the uploaded videos fetching part)
    # TODO: Make list have a sensible length and not subscriptions*25 (Currently mitigated by 'i')
    print(subfeed)
    for i, (date, video) in enumerate(subfeed.items()):
        # Cut off at a sensible length # FIXME: Hack
        if i > cutoff:
            break
        # TODO: Use longest title of current list, not entire subscriptions.
        print(longest_title)
        print(video)
        offset = longest_title - len(video['channel'])
        spacing = " " * offset + " " * 4

        print('%s\t%s%s\t%s:%s%s\t%s' % (video['date'], YT_VIDEO_URL, video['id'], video['channel'], spacing,
                                         video['title'], repr(video['description'])))


def print_stats_summary(time_list, indent=''):
    print(indent + "Fastest load: %s seconds." % min(time_list))
    print(indent + "Slowest load: %s seconds." % max(time_list))
    print(indent + "Average load: %s seconds." % float(fsum(time_list)/float(len(time_list))))


if __name__ == '__main__':
    global_debug = False
    global_info = False
    collect_statistics = True

    # Auth OAuth2 with YouTube API
    youtube = get_authenticated_service()

    # Get authenticated user's subscriptions
    timer_start = timer()
    # Get a list on the form of [total, subs, statistics]
    subscriptions = get_subscriptions(info=True, traverse_pages=False)
    subscription_total = subscriptions[0]
    subscription_list = subscriptions[1]
    timer_end = timer()

    subscriptions_statistics: dict = subscriptions[2]
    subscriptions_statistics['time_elapsed'] = (timer_end - timer_start)

    if subscription_total != len(subscription_list):
        print("WARNING: Subscription list mismatched advertised length (%s/%s)!" % (len(subscription_list),
                                                                                    subscription_total))

    # Process subscriptions and related data into a more manageable dict, TODO: Currently only used for longest_title
    subscribed_channels = process_subscriptions(subscription_list, info=False)

    # Fetch uploaded videos for each subscribed channel
    timer_start = timer()
    subscription_feed = get_uploads_all_channels(subscription_list, debug=False, disable_threading=False)  # FIXME: Re-using subscription_list?
    timer_end = timer()
    subfeed_time_elapsed = (timer_end - timer_start)

    # Print the subscription feed
    print_subscription_feed(subscription_feed, subscribed_channels['longest_title'], cutoff=100)

    if collect_statistics:
        print("\nSTATISTICS:")
        page_time = subscriptions_statistics['time_elapsed_page']
        page_total = subscriptions_statistics['time_elapsed']
        print("Subscriptions: Traversed %s pages of subscriptions in %s seconds" % (
            len(page_time), page_total))
        print_stats_summary(page_time, indent='\t')

        print("Subscription feed: Requested %s playlists in %s seconds." % (
            len(subscription_feed['statistics']), subfeed_time_elapsed))
        subfeed_time_elapsed_channels = []
        # Iterate a list of two-item dicts
        for item in subscription_feed['statistics']:
            # Append elapsed time statistics to a list
            subfeed_time_elapsed_channels.append(item['time_elapsed'])

        print_stats_summary(subfeed_time_elapsed_channels, indent='\t')
