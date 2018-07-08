import os
OS_PATH = os.path.dirname(__file__)

PICKLE_PATH = os.path.join(OS_PATH, 'resources', 'pickles')
THUMBNAIL_PATH = os.path.join(OS_PATH, 'resources', 'thumbnails')

if not os.path.isdir(PICKLE_PATH):
    os.makedirs(PICKLE_PATH)

if not os.path.isdir(THUMBNAIL_PATH):
    os.makedirs(THUMBNAIL_PATH)