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
        'miss_limit': '10',
        'test_pages': '2',
        'use_tests': 'True',
        'extra_list_pages': '0'
    },
    'Debug': {
        'debug': 'False',
        'cached_subs': 'True',
        'start_with_stored_videos': 'False',
        'channels_limit': '-1',
        'use_playlistitems': 'True',
        'disable_tqdm': 'True',
        'disable_tooltips': 'False',
        'show_grab_method': 'False'
    },
    'Gui': {
        'launch_gui': 'True',
        'hide_downloaded': 'True',
        'grid_view_x': '5',
        'grid_view_y': '4',
        'grey_old_videos': 'True',
        'enable_grid_resize': 'True',
        'tile_pref_height': '150',
        'tile_pref_width': '180'
    },
    'Thumbnails': {
        'force_download_best': 'True',
        '0': 'maxres',
        '1': 'standard',
        '2': 'high',
        '3': 'medium',
        '4': 'default'
    },
    'Threading': {
        'img_threads': '200',
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


def read_entire_config():
    """
    Reads the entire config file into a nested dict-list-dict
    :return:
    """
    config = {}
    for section in parser.sections():
        # print("[{}]".format(section))
        config[section] = []
        section_option = {}
        for option in parser.options(section):
            value = read_config(section, option)
            section_option[option] = value
            config[section].append(section_option)

    return config


def get_sections():
    """
    Returns config sections
    :return:
    """
    return parser.sections()


def get_options(section):
    """
    Returns config sections
    :return:
    """
    return parser.options(section)


def get_size():
    """
    Sums up sections and options
    :return:
    """
    size = 0
    for section in parser.sections():
        size += 1
        for option in parser.options(section):
            size += 1

    return size


def set_config(section, option, value):
    """
    Sets the givenm option's value
    :param section:
    :param option:
    :param value:
    :return:
    """
    parser.set(section, option, value)
    with open(CONFIG_PATH, 'w') as config:
        parser.write(config)

