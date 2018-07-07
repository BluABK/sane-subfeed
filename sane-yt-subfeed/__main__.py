from authentication import youtube_auth_keys, youtube_auth_oauth
from pickle_handler import load_youtube, dump_youtube, load_sub_list, dump_sub_list
from print_functions import print_subscription_feed
from timeit import default_timer

from uploads import Uploads
from youtube_requests import get_subscriptions

cached_subs = True
global_debug = False
global_info = False
info = True
debug = True
print_statistics = True
start = default_timer()


# Auth OAuth2 with YouTube API

# Create controller object

def cached_authenticated_get_subscriptions(cached):
    if cached:
        try:
            temp_subscriptions = load_sub_list()
        except FileNotFoundError:
            try:
                youtube_oauth = load_youtube()
            except FileNotFoundError:
                youtube_oauth = youtube_auth_oauth()
                dump_youtube(youtube_oauth)
            temp_subscriptions = get_subscriptions(youtube_oauth)
            dump_sub_list(temp_subscriptions)
    else:
        try:
            youtube_oauth = load_youtube()
            temp_subscriptions = get_subscriptions(youtube_oauth)
        except FileNotFoundError:
            youtube_oauth = youtube_auth_oauth()
            dump_youtube(youtube_oauth)
            temp_subscriptions = get_subscriptions(youtube_oauth)
    return temp_subscriptions


subscriptions = cached_authenticated_get_subscriptions(cached_subs)

# Get authenticated user's subscriptions
# Get a list on the form of [total, subs]
if info:
    print("Found %s subscriptions." % len(subscriptions))

# Print the channels in a subscription list
# subscribed_channels = controller.print_channels(subscription_list)

# Fetch uploaded videos for each subscribed channel
uploads = Uploads()
subscription_feed = uploads.get_uploads(subscriptions, info=True, debug=False, disable_threading=False)

# Print the subscription feed
print_subscription_feed(subscription_feed, cutoff=100)

time_elsapsed = default_timer() - start
print("\nRun time: {}".format(time_elsapsed))
