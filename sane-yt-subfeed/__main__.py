from controller import Controller
from authentication import youtube_auth_keys, youtube_auth_oauth
from timeit import default_timer as timer
from pickle_handler import load_youtube, dump_youtube

from uploads import Uploads

global_debug = False
global_info = False
collect_statistics = True

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
    controller.get_subscriptions(traverse_pages=False)
except Exception as e:
    print(e)
    youtube_oauth = youtube_auth_oauth()
    dump_youtube(youtube_oauth)
    controller = Controller(youtube_oauth)

# Get authenticated user's subscriptions
timer_start = timer()
# Get a list on the form of [total, subs, statistics]
subscriptions = controller.get_subscriptions(info=True, traverse_pages=True)
subscription_total = subscriptions[0]
subscription_list = subscriptions[1]
timer_end = timer()

subscriptions_statistics: dict = subscriptions[2]
subscriptions_statistics['time_elapsed'] = (timer_end - timer_start)

if subscription_total != len(subscription_list):
    print("WARNING: Subscription list mismatched advertised length (%s/%s)!" % (len(subscription_list),
                                                                                subscription_total))

# Process subscriptions and related data into a more manageable dict, TODO: Currently only used for longest_title
subscribed_channels = controller.process_subscriptions(subscription_list, info=False)

youtube_key = youtube_auth_keys()
# Fetch uploaded videos for each subscribed channel
timer_start = timer()
uploads = Uploads(youtube_key)
subscription_feed = uploads.get_uploads(subscription_list, info=True, debug=False, disable_threading=False)
# subscription_feed = controller.get_uploads_all_channels(subscription_list, debug=False, disable_threading=False)  # FIXME: Re-using subscription_list?
timer_end = timer()
subfeed_time_elapsed = (timer_end - timer_start)

# Print the subscription feed
controller.print_subscription_feed(subscription_feed, subscribed_channels['longest_title'], cutoff=100)

if collect_statistics:
    print("\nSTATISTICS:")
    page_time = subscriptions_statistics['time_elapsed_page']
    page_total = subscriptions_statistics['time_elapsed']
    print("Subscriptions: Traversed %s pages of subscriptions in %s seconds" % (
        len(page_time), page_total))
    controller.print_stats_summary(page_time, indent='\t')

    print("Subscription feed: Requested %s playlists in %s seconds." % (    # FIXME: Ridiculously inflated number
        len(subscription_feed['statistics']), subfeed_time_elapsed))
    subfeed_time_elapsed_channels = []
    # Iterate a list of two-item dicts
    for item in subscription_feed['statistics']:
        # Append elapsed time statistics to a list
        subfeed_time_elapsed_channels.append(item['time_elapsed'])

    controller.print_stats_summary(subfeed_time_elapsed_channels, indent='\t')