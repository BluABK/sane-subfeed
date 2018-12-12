import os
import json

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from sane_yt_subfeed.log_handler import create_logger

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)

OS_PATH = os.path.dirname(__file__)

CLIENT_SECRET_FILE = os.path.join(OS_PATH, 'resources', 'client_secret.json')
KEYS_FILE = os.path.join(OS_PATH, 'resources', 'keys.json')
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_api_key():
    with open(KEYS_FILE) as keys_json_data_file:
        keys = json.load(keys_json_data_file)
    return keys['api_key']


def youtube_auth_oauth():
    """
    Authorize the request and store authorization credentials.
    :return:
    """
    logger.info("OAuth: Authorising API...")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_console()
    logger.info("OAuth: Instantiated flow (console)")
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def youtube_auth_keys():
    logger.info("Keys: Authorising API...")
    return build(API_SERVICE_NAME, API_VERSION, developerKey=get_api_key())
