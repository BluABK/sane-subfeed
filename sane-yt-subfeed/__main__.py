from controller import Controller
from authentication import youtube_auth_keys, youtube_auth_oauth
from pickle_handler import load_youtube, dump_youtube
from statistic import Statistic, all_statistics

from uploads import Uploads

global_debug = False
global_info = False
info = True
debug = True
print_statistics = True

try:
    youtube_oauth = load_youtube()
except Exception as e:
    print(e)
    youtube_oauth = youtube_auth_oauth()
    dump_youtube(youtube_oauth)


# Auth OAuth2 with YouTube API

# Create controller object
controller = Controller(youtube_oauth)

try:
    controller.get_subscriptions(traverse_pages=False, stats=False)
except ValueError as abks_exception:
    raise abks_exception
except Exception as e:
    print(e)
    youtube_oauth = youtube_auth_oauth()
    dump_youtube(youtube_oauth)
    controller = Controller(youtube_oauth)

# Get authenticated user's subscriptions
stat_get_subs = Statistic("Subscriptions (GET): Total runtime", timer=True)

# Get a list on the form of [total, subs]
subscriptions = controller.get_subscriptions(info=True, traverse_pages=False)
if info:
    print("Found %s subscriptions." % len(subscriptions))
stat_get_subs.stop_timer()


# Print the channels in a subscription list
# subscribed_channels = controller.print_channels(subscription_list)

youtube_key = youtube_auth_keys()
# Fetch uploaded videos for each subscribed channel
stat_get_uploads = Statistic("Uploads (GET): Total runtime", timer=True)
uploads = Uploads(youtube_key)
subscription_feed = uploads.get_uploads(subscriptions, info=True, debug=False, disable_threading=False)
stat_get_uploads.stop_timer()

# Print the subscription feed
controller.print_subscription_feed(subscription_feed, cutoff=100)

"""
    print("\nSTATISTICS:")
    page_time = subscriptions_statistics['time_elapsed_page']
    page_total = subscriptions_statistics['time_elapsed']
    print("Subscriptions: Traversed %s pages of subscriptions in %s seconds" % (
        len(page_time), page_total))
    controller.print_stats_summary(page_time, indent='\t')

    print("Subscription feed: Requested %s playlists in %s seconds." % (    # FIXME: Ridiculously inflated number
        len(subscription_feed_statistics), subfeed_time_elapsed))
    subfeed_time_elapsed_channels = []
    # Iterate a list of two-item dicts
    for item in subscription_feed_statistics:
        # Append elapsed time statistics to a list
        subfeed_time_elapsed_channels.append(item['time_elapsed'])
"""
print_statistics = False
if print_statistics:
    print("\nSTATISTICS:")
    for stat in all_statistics:
        stat.print_stats_summary(indent='\t')

    # controller.print_stats_summary(subfeed_time_elapsed_channels, indent='\t')
