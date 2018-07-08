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
    },
    'Gui': {
        'launch': 'Gui',
    },
    'Thumbnails': {
        '0': 'default',
        '1': 'medium',
        '2': 'high',
        '3': 'standard',
        '4': 'maxres'
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
        return value
    else:
        return defaults[section][option]


def set_config(section, key, value):
    parser.set(section, key, value)

