import os

# Backend
ROOT_PATH = os.path.dirname(__file__)
RESOURCES_PATH = os.path.join(ROOT_PATH, 'resources')

# YouTube
CLIENT_SECRET_FILE = os.path.join(ROOT_PATH, 'resources', 'client_secret.json')
KEYS_FILE = os.path.join(ROOT_PATH, 'resources', 'keys.json')

# GUI
ICONS_PATH = os.path.join(ROOT_PATH, 'resources', 'icons')
VERSION_PATH = os.path.join(ROOT_PATH, '..', 'VERSION')
