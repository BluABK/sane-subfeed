import os
from PyQt5.QtWidgets import QStyleFactory

from sane_yt_subfeed.absolute_paths import RESOURCES_PATH

THEME_PATH = os.path.join(RESOURCES_PATH, 'themes')

UNSET_THEME = None  # Sending in NoneType will reset to defaults.

BREEZE_ROOT = os.path.join(THEME_PATH, 'breeze')
BREEZE_LIGHT = os.path.join(BREEZE_ROOT, 'light.qss')
BREEZE_DARK = os.path.join(BREEZE_ROOT, 'dark.qss')
BREEZE_LIGHT_WINDOWS_MOD = os.path.join(BREEZE_ROOT, 'light-windows-mod.qss')
BREEZE_DARK_WINDOWS_MOD = os.path.join(BREEZE_ROOT, 'dark-windows-mod.qss')

CUSTOM_ROOT = os.path.join(THEME_PATH, 'custom')
CUSTOM_THEMES_AVAILABLE = []
for custom_style_filename in os.listdir(CUSTOM_ROOT):
    if custom_style_filename.endswith('.qss'):
        CUSTOM_THEMES_AVAILABLE.append({'name': custom_style_filename,
                                        'path': os.path.join(CUSTOM_ROOT, custom_style_filename)})

THEMES_AVAILABLE = {'linux': [UNSET_THEME, BREEZE_LIGHT, BREEZE_DARK],
                    'windows': [UNSET_THEME, BREEZE_LIGHT_WINDOWS_MOD, BREEZE_DARK_WINDOWS_MOD]
                    }

QSTYLES_AVAILABLE = {}
qsf = QStyleFactory()
# Populate the QStyle dict
for style in qsf.keys():
    QSTYLES_AVAILABLE[style] = qsf.create(style)
del qsf
