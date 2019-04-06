import os

# Backend
ROOT_PATH = os.path.dirname(__file__)
PROJECT_ROOT_PATH = os.path.join(ROOT_PATH, '..')
RESOURCES_PATH = os.path.join(ROOT_PATH, 'resources')
IMG_PATH = os.path.join(ROOT_PATH, 'images')

# Database
DATABASE_PATH = os.path.join(RESOURCES_PATH, 'permanents.db')

# Config
CONFIG_PATH = os.path.join(PROJECT_ROOT_PATH, 'config.ini')
CONFIG_HOTKEYS_PATH = os.path.join(PROJECT_ROOT_PATH, 'hotkeys.ini')
SAMPLE_HOTKEYS_PATH = os.path.join(PROJECT_ROOT_PATH, 'hotkeys.ini.sample')
SAMPLE_PATH = os.path.join(PROJECT_ROOT_PATH, 'config.ini.sample')

# Logs
LOG_DIR = os.path.join(PROJECT_ROOT_PATH, 'logs')

# Plaintext history
HISTORY_FILE_PATH = os.path.join(LOG_DIR, 'history.txt')

# Pickler
PICKLE_PATH = os.path.join(RESOURCES_PATH, 'pickles')
YOUTUBE_RESOURCE_OAUTH_PICKLE = os.path.join(PICKLE_PATH, 'youtube_oauth.pkl')
YOUTUBE_RESOURCE_KEYS_PICKLE = os.path.join(PICKLE_PATH, 'youtube_auth_keys.pkl')

# YouTube
CLIENT_SECRET_FILE = os.path.join(RESOURCES_PATH, 'client_secret.json')
CLIENT_SECRET_PUBLIC_FILE = os.path.join(RESOURCES_PATH, "client_secret_public.json")
KEYS_FILE = os.path.join(RESOURCES_PATH, 'keys.json')
KEYS_PULIC_FILE = os.path.join(RESOURCES_PATH, "keys_public.json")

THUMBNAILS_PATH = os.path.join(RESOURCES_PATH, 'thumbnails')
THUMBNAILS_RESIZED_PATH = os.path.join(THUMBNAILS_PATH, 'resized')
THUMBNAIL_NA_PATH = os.path.join(RESOURCES_PATH, 'thumbnail_na.png')
THUMBNAIL_404_PATH = os.path.join(RESOURCES_PATH, 'quality404.jpg')

# GUI
ICONS_PATH = os.path.join(RESOURCES_PATH, 'icons')
VERSION_PATH = os.path.join(PROJECT_ROOT_PATH, 'VERSION')
OVERLAY_NEW_PATH = os.path.join(ICONS_PATH, 'new_vid.png')
OVERLAY_MISSED_PATH = os.path.join(ICONS_PATH, 'missed_vid.png')
OVERLAY_DOWNLOADED_PATH = os.path.join(ICONS_PATH, 'downloaded_vid.png')
OVERLAY_DISCARDED_PATH = os.path.join(ICONS_PATH, 'dismissed.png')
OVERLAY_WATCHED_PATH = os.path.join(ICONS_PATH, 'watched.png')
OVERLAY_NO_FILE_PATH = os.path.join(ICONS_PATH, 'no_file.png')
ABOUT_IMG_PATH = os.path.join(IMG_PATH, 'about.png')
DUMMY_ICO_PATH = os.path.join(ICONS_PATH, 'dummies')