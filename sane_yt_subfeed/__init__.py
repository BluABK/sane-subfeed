import os

from PyQt5 import QtCore

from sane_yt_subfeed.database.orm import init_db
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.history_handler import HISTORY_FILEPATH

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)
logger.info("Initializing...")

OS_PATH = os.path.dirname(__file__)

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
