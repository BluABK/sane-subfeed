import os

from PyQt5 import QtCore

from sane_yt_subfeed.database.orm import init_db

OS_PATH = os.path.dirname(__file__)

PICKLE_PATH = os.path.join(OS_PATH, 'resources', 'pickles')
THUMBNAIL_PATH = os.path.join(OS_PATH, 'resources', 'thumbnails')

PYQT_PATH = os.path.join(OS_PATH, '..', 'env', 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins')
PYQT_PATH2 = os.path.join(OS_PATH, 'env', 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins')

QtCore.QCoreApplication.addLibraryPath(PYQT_PATH)
QtCore.QCoreApplication.addLibraryPath(PYQT_PATH2)

init_db()


if not os.path.isdir(PICKLE_PATH):
    os.makedirs(PICKLE_PATH)

if not os.path.isdir(THUMBNAIL_PATH):
    os.makedirs(THUMBNAIL_PATH)