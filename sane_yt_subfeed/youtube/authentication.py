import apiclient
import httplib2
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauthlib.oauth2 import MissingCodeError

from sane_yt_subfeed.absolute_paths import KEYS_FILE, CLIENT_SECRET_FILE
from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.settings import mutable_settings

logger = create_logger(__name__)

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_api_key():
    with open(KEYS_FILE) as keys_json_data_file:
        keys = json.load(keys_json_data_file)
    return keys['api_key']


def build_request(http, *args, **kwargs):
    """
    The httplib2.Http() objects are not thread-safe. Create a new Http() object for every request and
    override the construction of it within the service object.

    https://developers.google.com/api-client-library/python/guide/thread_safety
    :param http:
    :param args:
    :param kwargs:
    :return:
    """
    new_http = httplib2.Http()
    return apiclient.http.HttpRequest(new_http, *args, **kwargs)


def youtube_auth_oauth():
    """
    Authorize the request using OAuth and store authorization credentials.

    OAuth is required for most higher level user actions like accessing user's subscriptions.
    :return:
    """
    logger.info("OAuth: Authorising API...")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    if mutable_settings.using_gui:
        try:
            credentials = flow.run_local_server(host='localhost',
                                                port=read_config('Authentication', 'oauth2_local_server_port',
                                                                 literal_eval=True),
                                                authorization_prompt_message='Please visit this URL: {url}',
                                                success_message='The auth flow is complete; you may close this window.',
                                                open_browser=True)
        except MissingCodeError as exc_mce:
            logger.exception("A MissingCodeError Exception occurred during OAuth2",
                             exc_info=exc_mce)
            return None

    else:
        credentials = flow.run_console()
    logger.info("OAuth: Instantiated flow (console)")
    # Note: If you try to send in requestBuilder here it will fail, but OAuth isn't threaded so it should be fine...
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def youtube_auth_keys():
    """
    Authorize the request using an API Key and store authorization credentials.

    API Keys are easier to use than needing to OAuth for every single resource.
    :return:
    """
    logger.info("Keys: Authorising API...")
    # Send in requestBuilder to override the construction of non-thread safe http obj within the service object.
    return build(API_SERVICE_NAME, API_VERSION, developerKey=get_api_key(), requestBuilder=build_request)
