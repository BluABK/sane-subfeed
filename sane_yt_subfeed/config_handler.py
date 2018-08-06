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
    'Model': {
        'loaded_videos': '200'
    },
    'Requests': {
        'miss_limit': '10',
        'test_pages': '2',
        'use_tests': 'True',
        'extra_list_pages': '0',
        'deep_search_quota_k': '20'
    },
    'Debug': {
        'debug': 'False',
        'cached_subs': 'True',
        'start_with_stored_videos': 'False',
        'channels_limit': '-1',
        'use_playlistitems': 'True',
        'disable_tqdm': 'True',
        'disable_tooltips': 'False',
        'show_grab_method': 'False',
        'log_search': 'False',
        'log_list': 'False',
        'log_needle': 'unset',
        'show_unimplemented_gui': 'False'
    },
    'Gui': {
        'launch_gui': 'True',
        'hide_downloaded': 'True',
        'grid_view_x': '5',
        'grid_view_y': '4',
        'grey_old_videos': 'True',
        'tile_pref_height': '150',
        'tile_pref_width': '180',
        'tooltip_pictures': 'False',
        'tooltip_picture_width': '512',
        'tooltip_picture_height': '256',
        'tooltip_picture_size': 'h1',
        'keep_thumb_ar': 'False',
        'enable_auto_copy_to_clipboard': 'False'
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
    },
    'Play': {
        'yt_file_path': "",
        'disable_dir_listener': 'False',
    },
    'Youtube-dl': {
        'use_youtube_dl': 'True'
    },
    'Player': {
        'default_player': "",
        'alternative_player1': "",
        'alternative_player2': "",
        'alternative_player3': ""
    },
    'Logging': {
        'use_socket_log': 'False'
    }
}


def read_config(section, option, literal_eval=True):
    if literal_eval:
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
    else:
        if not os.path.exists(CONFIG_PATH):
            copyfile(SAMPLE_PATH, CONFIG_PATH)
        try:
            value = parser.get(section, option)
        except (NoSectionError, NoOptionError):
            value = defaults[section][option]
        if value:
            try:
                return value
            except ValueError:
                return value
        else:
            return defaults[section][option]



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

