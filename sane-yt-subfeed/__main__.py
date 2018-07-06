from controller import Controller
from authentication import youtube_auth_keys, youtube_auth_oauth
from pickle_handler import load_youtube, dump_youtube

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
# Get a list on the form of [total, subs]
subscriptions = controller.get_subscriptions(info=True, traverse_pages=True)
if info:
    print("Found %s subscriptions." % len(subscriptions))


# Print the channels in a subscription list
# subscribed_channels = controller.print_channels(subscription_list)

youtube_key = youtube_auth_keys()
# Fetch uploaded videos for each subscribed channel
uploads = Uploads(youtube_key)
subscription_feed = uploads.get_uploads(subscriptions, info=True, debug=False, disable_threading=False)

# Print the subscription feed
controller.print_subscription_feed(subscription_feed, cutoff=100)