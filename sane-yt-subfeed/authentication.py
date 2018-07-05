import os

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

OS_PATH = os.path.dirname(__file__)

CLIENT_SECRETS_FILE = os.path.join(OS_PATH, 'resources', 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
API_KEY = ''


def youtube_auth_oauth():
    """
    Authorize the request and store authorization credentials.
    :return:
    """
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def youtube_auth_keys():
    print('youtube_auth_keys')
    return build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
