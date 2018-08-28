import ast
import os
from shutil import copyfile
from configparser import ConfigParser, NoSectionError, NoOptionError

OS_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(OS_PATH, '..', 'config.ini')
CONFIG__HOTKEYS_PATH = os.path.join(OS_PATH, '..', 'hotkeys.ini')
SAMPLE_HOTKEYS_PATH = os.path.join(OS_PATH, '..', 'hotkeys.ini.sample')
SAMPLE_PATH = os.path.join(OS_PATH, '..', 'config.ini.sample')

parser = None
default_parser = ConfigParser()
default_parser.read(CONFIG_PATH)
hotkeys_parser = ConfigParser()
hotkeys_parser.read(CONFIG_PATH)

DEFAULTS = {
    'Model': {
        'loaded_videos': '200'
    },
    'Requests': {
        'miss_limit': '10',
        'test_pages': '2',
        'use_tests': 'True',
        'extra_list_pages': '0',
        'deep_search_quota_k': '20',
        'filter_videos_days_old': '-1'
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
    'Theme': {
        'last_style': "",
        'last_theme': ""
    },
    'GridView': {
        'show_watched': 'False',
        'show_dismissed': 'False',
        'title_tile_pixel_size': '0.40'
    },
    'SubFeed': {
        'show_downloaded': 'False',
    },
    'DownloadView': {
        'download_tile_height': '200'
    },
    'PlaySort': {
        'ascending_date': 'False'
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
        'use_url_as_path': 'False',
        'default_watch_prio': '10'
    },
    'Youtube-dl': {
        'use_youtube_dl': 'True'
    },
    'Youtube-dl_proxies': {
        'proxy1': "",
        'proxy2': "",
        'proxy3': "",
        'proxy4': "",
        'proxy5': ""
    },
    'Youtube-dl_opts': {},
    'Player': {
        'default_player': "",
        'alternative_player1': "",
        'alternative_player2': "",
        'alternative_player3': "",
        'url_player': ""
    },
    'DefaultApp': {
      'Image': ""
    },
    'Logging': {
        'use_socket_log': 'False',
        'log_level': '1',
        'logging_port': '19996'
    }
}

DEFAULTS_HOTKEYS = {
    'Global': {
        'preferences': 'Ctrl+P',
        'quit': 'Ctrl+Q',
        'copy_all_urls': 'Ctrl+D',
        'refresh_feed': 'Ctrl+R',
        'reload_subslist': 'Ctrl+L',
        'test_channels': "",
        'manual_dir_search': "",
        'manual_thumb_dl': "",
        'manual_db_grab': 'Ctrl+E',
        'download_video_by_url': 'Ctrl+O',
        'show_usage_history': 'Ctrl+H'
    },
    'View': {
        'subfeed': 'Ctrl+1',
        'playback': 'Ctrl+2',
        'detailed_list': 'Ctrl+3',
        'subscriptions': 'Ctrl+5'
    },
    'Subfeed': {
        'download': 'LeftButton',
        'dismiss': 'MidButton'
    },
    'Playback': {
        'prio_decrease': 'MidButton, Ctrl+LeftButton',
        'mark_watched': 'Alt+LeftButton',
        'play': 'MouseLeftButton',
        'ascending_sort_toggle': 'Ctrl+A'
    }
}


def read_config(section, option, literal_eval=True, custom_ini=None):
    """
    Reads a configuration file (INI format)
    :param section:
    :param option:
    :param literal_eval: eval config literally, instead of string
    :param custom_ini: if set, use given custom config
    :return:
    """
    config_path = CONFIG_PATH
    sample_path = SAMPLE_PATH
    defaults = DEFAULTS
    parser = default_parser
    # Support multiple configs
    if custom_ini is not None:
        # logger.debug("Reading custom config: {}".format(custom_ini))
        if custom_ini == "hotkeys":
            config_path = CONFIG__HOTKEYS_PATH
            sample_path = SAMPLE_HOTKEYS_PATH
            defaults = DEFAULTS_HOTKEYS
            parser = hotkeys_parser
        else:
            # logger.critical("Custom config '{}' is not defined in handler!!".format(custom_ini))
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))

    if literal_eval:
        if not os.path.exists(config_path):
            copyfile(sample_path, config_path)
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
        if not os.path.exists(config_path):
            copyfile(sample_path, config_path)
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


def read_entire_config(custom_ini=None):
    """
    Reads the entire config file into a nested dict-list-dict
    :return:
    """
    _parser = default_parser
    if custom_ini is not None:
        if custom_ini == "hotkeys":
            _parser = hotkeys_parser
        else:
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))

    config = {}
    for section in _parser.sections():
        # print("[{}]".format(section))
        config[section] = []
        section_option = {}
        for option in _parser.options(section):
            value = read_config(section, option)
            section_option[option] = value
            config[section].append(section_option)

    return config


def has_section(section, custom_ini=None):
    """
    Checks if a section exists in config
    :return:
    """
    _parser = default_parser
    if custom_ini is not None:
        if custom_ini == "hotkeys":
            _parser = hotkeys_parser
        else:
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))
    return _parser.has_section(section)


def get_sections(custom_ini=None):
    """
    Returns config sections
    :return:
    """
    _parser = default_parser
    if custom_ini is not None:
        if custom_ini == "hotkeys":
            _parser = hotkeys_parser
        else:
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))

    return _parser.sections()


def get_options(section, custom_ini=None):
    """
    Returns config sections
    :return:
    """
    _parser = default_parser
    if custom_ini is not None:
        if custom_ini == "hotkeys":
            _parser = hotkeys_parser
        else:
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))

    return _parser.options(section)


def get_size(custom_ini=None, incl_sections=False):
    """
    Sums up sections and options
    :return:
    """
    _parser = default_parser
    if custom_ini is not None:
        if custom_ini == "hotkeys":
            _parser = hotkeys_parser
        else:
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))

    size = 0
    for section in _parser.sections():
        if incl_sections:
            size += 1
        for _ in _parser.options(section):
            size += 1

    return size


def set_config(section, option, value, custom_ini=None):
    """
    Sets the givenm option's value
    :param custom_ini:
    :param section:
    :param option:
    :param value:
    :return:
    """
    if value is None:
        value = ""  # Keep a uniform format in the config
    _parser = default_parser
    if custom_ini is not None:
        if custom_ini == "hotkeys":
            _parser = hotkeys_parser
        else:
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))

    try:
        _parser.set(section, option, value)
    except NoSectionError:
        _parser.add_section(section)
        _parser.set(section, option, value)
    with open(CONFIG_PATH, 'w') as config:
        _parser.write(config)
