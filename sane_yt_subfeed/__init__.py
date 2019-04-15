import os
from PyQt5 import QtCore

from sane_yt_subfeed.absolute_paths import HISTORY_FILE_PATH, LOG_DIR
from sane_yt_subfeed.database.orm import init_db
from sane_yt_subfeed.handlers.log_handler import create_logger

logger = create_logger(__name__)
logger.info("Initializing...")

OS_PATH = os.path.dirname(__file__)

PICKLE_PATH = os.path.join(OS_PATH, 'resources', 'pickles')
THUMBNAIL_PATH = os.path.join(OS_PATH, 'resources', 'thumbnails')

# Required on windows (w/ virtualenv)
PYQT_PATH = os.path.join(OS_PATH, '..', 'env', 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins')
PYQT_PATH2 = os.path.join(OS_PATH, 'env', 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins')

QtCore.QCoreApplication.addLibraryPath(PYQT_PATH)
QtCore.QCoreApplication.addLibraryPath(PYQT_PATH2)

# Initialize database
init_db()

# Make sure dirs exists on startup
if not os.path.isdir(PICKLE_PATH):
    os.makedirs(PICKLE_PATH)

if not os.path.isdir(THUMBNAIL_PATH):
    os.makedirs(THUMBNAIL_PATH)

if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

# Make sure files exists on startup
if not os.path.isfile(HISTORY_FILE_PATH):
    open(HISTORY_FILE_PATH, 'a').close()
