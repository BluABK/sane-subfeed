import ast
import os
from shutil import copyfile
from configparser import ConfigParser, NoSectionError, NoOptionError

OS_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(OS_PATH, '..', 'config.ini')
SAMPLE_PATH = os.path.join(OS_PATH, '..', 'config.ini.sample')

parser = ConfigParser()
parser.read(CONFIG_PATH)

defaults = {
    'Requests': {
    },
    'Debug': {
        'debug': 'False',
        'cached_subs': 'True',
        'start_with_stored_videos': 'False',
        'channels_limit': '-1',
        'use_playlistItems': 'True',
        'disable_tqdm': 'True',
        'disable_tooltips': 'False'
    },
    'Gui': {
        'launch': 'Gui',
        'hide_downloaded': 'True'
    },
    'Thumbnails': {
        'force_download_best': 'False',
        '0': 'maxres',
        '1': 'standard',
        '2': 'high',
        '3': 'medium',
        '4': 'default'
    },
    'Threading': {
        'img_threads': '100',
    }
}


def read_config(section, option):
    if not os.path.exists(CONFIG_PATH):
        copyfile(SAMPLE_PATH, CONFIG_PATH)
    try:
        value = parser.get(section, option)
    except (NoSectionError, NoOptionError):
        value = defaults[section][option]
    if value:
        try:
            return ast.literal_eval(value)
        except ValueError:
            return value
    else:
        return ast.literal_eval(defaults[section][option])


def set_config(section, key, value):
    parser.set(section, key, value)

