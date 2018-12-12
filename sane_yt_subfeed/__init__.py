import os
import shutil  # For file copying

from PyQt5 import QtCore

from sane_yt_subfeed.database.orm import init_db
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.history_handler import HISTORY_FILEPATH

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)
logger.info("Initializing...")

OS_PATH = os.path.dirname(__file__)

CLIENT_SECRET_FILE = os.path.join(OS_PATH, 'resources', 'client_secret.json')
KEYS_FILE = os.path.join(OS_PATH, 'resources', 'keys.json')

PICKLE_PATH = os.path.join(OS_PATH, 'resources', 'pickles')
THUMBNAIL_PATH = os.path.join(OS_PATH, 'resources', 'thumbnails')

PYQT_PATH = os.path.join(OS_PATH, '..', 'env', 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins')
PYQT_PATH2 = os.path.join(OS_PATH, 'env', 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins')

QtCore.QCoreApplication.addLibraryPath(PYQT_PATH)
QtCore.QCoreApplication.addLibraryPath(PYQT_PATH2)

init_db()

# Make sure dirs exists on startup
if not os.path.isdir(PICKLE_PATH):
    os.makedirs(PICKLE_PATH)

if not os.path.isdir(THUMBNAIL_PATH):
    os.makedirs(THUMBNAIL_PATH)

# Make sure files exists on startup
if not os.path.isfile(HISTORY_FILEPATH):
    open(HISTORY_FILEPATH, 'a').close()

if not os.path.isfile(KEYS_FILE):
    logger.warning("keys.json file was not found: Installing public version.")
    shutil.copyfile(os.path.join(OS_PATH, "resources", "keys_public.json"),
                    KEYS_FILE)

if not os.path.isfile(CLIENT_SECRET_FILE):
    logger.warning("client_secret.json file was not found: Installing public version.")
    shutil.copyfile(os.path.join(OS_PATH, "resources", "client_secret_public.json"),
                    CLIENT_SECRET_FILE)
