import os

from PyQt5.QtWidgets import QStyleFactory

from sane_yt_subfeed.absolute_paths import RESOURCES_PATH

from sane_yt_subfeed.resources.themes.breeze import breeze_resouces

THEME_PATH = os.path.join(RESOURCES_PATH, 'themes')

BREEZE_ROOT = os.path.join(THEME_PATH, 'breeze')
BREEZE_LIGHT = os.path.join(BREEZE_ROOT, 'light.qss')
BREEZE_DARK = os.path.join(BREEZE_ROOT, 'dark.qss')

BREEZE_DARK_FILENAME = 'dark.qss'
BREEZE_LIGHT_FILENAME = 'light.qss'

THEMES_LIST = [None, BREEZE_LIGHT, BREEZE_DARK]
QSTYLES_AVAILABLE = {}

# Populate the QStyle dict
for style in QStyleFactory.keys():
    QSTYLES_AVAILABLE[style] = QStyleFactory.create(style)
