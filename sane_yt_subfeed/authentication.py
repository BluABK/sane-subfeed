import os
import json
import shutil  # For file copying

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from sane_yt_subfeed.log_handler import create_logger

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)

OS_PATH = os.path.dirname(__file__)

CLIENT_SECRETS_FILE = os.path.join(OS_PATH, 'resources', 'client_secret.json')
KEYS_FILE = os.path.join(OS_PATH, 'resources', 'keys.json')
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def handle_missing_keys():
    """
    Checks if a keys.json exists in the expected location, if it does not then copy the public version.
    :return:
    """
    if not os.path.isfile(KEYS_FILE):
        logger.warning("keys.json file was not found: Installing public version.")
        shutil.copyfile(os.path.join(OS_PATH, "resources", "keys_public.json"),
                        KEYS_FILE)


def get_api_key():
    handle_missing_keys()
    with open(KEYS_FILE) as keys_json_data_file:
        keys = json.load(keys_json_data_file)
    return keys['api_key']


def youtube_auth_oauth():
    """
    Authorize the request and store authorization credentials.
    :return:
    """
    logger.info("OAuth: Authorising API...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    except FileNotFoundError as exc_fnfe:
        logger.warning("client_secret.json file was not found: Installing public version.")
        if "client_secret.json" in str(exc_fnfe):
            shutil.copyfile(os.path.join(OS_PATH, "resources", "client_secret_public.json"),
                            os.path.join(OS_PATH, "resources", "client_secret.json"))

            # Retry InstalledAppFlow creation
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        else:
            logger.critical("Unhandled FileNotFound Exception in youtube_auth_oauth()", exc_info=exc_fnfe)
            raise
    credentials = flow.run_console()
    logger.info("OAuth: Instantiated flow (console)")
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def youtube_auth_keys():
    logger.info("Keys: Authorising API...")
    return build(API_SERVICE_NAME, API_VERSION, developerKey=get_api_key())
