import os

# Backend
ROOT_PATH = os.path.dirname(__file__)
RESOURCES_PATH = os.path.join(ROOT_PATH, 'resources')

# Pickler
PICKLE_PATH = os.path.join(ROOT_PATH, 'resources', 'pickles')
YOUTUBE_RESOURCE_OAUTH_PICKLE = os.path.join(PICKLE_PATH, 'youtube_oauth.pkl')
YOUTUBE_RESOURCE_KEYS_PICKLE = os.path.join(PICKLE_PATH, 'youtube_auth_keys.pkl')

# YouTube
CLIENT_SECRET_FILE = os.path.join(ROOT_PATH, 'resources', 'client_secret.json')
KEYS_FILE = os.path.join(ROOT_PATH, 'resources', 'keys.json')

# GUI
ICONS_PATH = os.path.join(ROOT_PATH, 'resources', 'icons')
VERSION_PATH = os.path.join(ROOT_PATH, '..', 'VERSION')
