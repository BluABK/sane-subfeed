import ast
import copy
import os
from configparser import ConfigParser, NoSectionError, NoOptionError
from sane_yt_subfeed.absolute_paths import CONFIG_PATH, SAMPLE_PATH, CONFIG_HOTKEYS_PATH, \
    SAMPLE_HOTKEYS_PATH, DATABASE_PATH

parser = None
default_parser = ConfigParser()
default_parser.read(CONFIG_PATH)
hotkeys_parser = ConfigParser()
hotkeys_parser.read(CONFIG_HOTKEYS_PATH)

DEFAULTS = {
    'Model': {
        'loaded_videos': '90'
    },
    'Requests': {
        'miss_limit': '10',
        'test_pages': '2',
        'use_tests': 'True',
        'extra_list_pages': '3',
        'deep_search_quota_k': '100',
        'filter_videos_days_old': '-1'
    },
    'Debug': {
        'debug': 'False',
        'cached_subs': 'True',
        'start_with_stored_videos': 'True',
        'channels_limit': '-1',
        'use_playlistitems': 'True',
        'disable_tooltips': 'False',
        'show_unimplemented_gui': 'False',
        'display_all_exceptions': 'False',
        'color_tile_elements': 'False'
    },
    'Gui': {
        'launch_gui': 'True',
        'grid_view_x': '6',
        'grid_view_y': '5',
        'grey_old_videos': 'False',
        'tile_pref_height': '209',
        'tile_pref_width': '209',
        'tile_overlay_height_pct': '30',
        'tile_overlay_width_pct': '70',
        'tooltip_pictures': 'False',
        'tooltip_picture_width': '512',
        'tooltip_picture_height': '256',
        'tooltip_picture_size': 'h1',
        'keep_thumb_ar': 'True',
        'enable_auto_copy_to_clipboard': 'False',
        'bgcolor': "",
        'darkmode_icons': 'False',
        'toolbar_icon_size_modifier': '1'
    },
    'Theme': {
        'last_style': "",
        'last_theme': ""
    },
    'Fonts': {
        'video_title_font': 'Noto Sans,10,-1,0,75,0,0,0,0,0,Bold',
        'video_channel_font': 'Noto Sans,10,-1,0,50,0,0,0,0,0,Regular',
        'video_date_font': 'Noto Sans,10,-1,0,50,0,0,0,0,0,Regular',
        'video_thumbnail_overlay_font': 'Noto Sans,10,-1,0,50,0,0,0,0,0,Regular'
    },
    'GridView': {
        'show_watched': 'False',
        'show_dismissed': 'False',
        'show_sd_warning': 'False',
        'show_has_captions': 'True',
        'elided_text_modifier_title': '1',
        'elided_text_modifier_channel': '1',
        'elided_text_modifier_date': '1',
        'elided_text_unicode_weight_modifier': '0.0075',
        'tile_unicode_line_height_offset': '1.99',
        'tile_line_spacing': '5',
        'tile_title_lines': '2',
        'tile_channel_lines': '1',
        'tile_date_lines': '1',
        'title_tile_font_weight': 'Bold',
        'timedelta_format': '$HH:$MM:$SS ago',
        'timedelta_format_days': '$d days, $HH:$MM:$SS ago',
        'timedelta_format_months': '$m months, ${d}d, $HH:$MM:$SS ago',
        'timedelta_format_years': '${yd}y, ${m}m, ${d}d, $HH:$MM:$SS ago',
        'timedelta_format_decades': '${decades}dc, ${yd}y, ${m}m, ${d}d, $HH:$MM:$SS ago'
    },
    'SubFeed': {
        'show_downloaded': 'False',
        'color_live_broadcast_content': 'True',
        'left_mouse_action': 'Open URL in browser'
    },
    'DownloadView': {
        'download_tile_height': '200'
    },
    'PlaySort': {
        'ascending_date': 'False',
        'by_channel': 'False'
    },
    'SubSort': {
        'ascending_date': 'False',
        'by_channel': 'False',
        'pin_live_broadcast_content': 'True'
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
        'retry_attempts': '10',
        'retry_delay': '1.0'
    },
    'Play': {
        'enabled': 'False',
        'yt_file_path': "",
        'disable_dir_listener': 'False',
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
    'Postprocessing': {
        'prefer_ffmpeg': 'True',
        'ffmpeg_location': "",
        'embed_metadata': 'False'
    },
    'Player': {
        'default_player': "",
        'alternative_player1': "",
        'alternative_player2': "",
        'alternative_player3': "",
        'alternative_player4': "",
        'alternative_player5': "",
        'alternative_player6': "",
        'alternative_player7': "",
        'alternative_player8': "",
        'alternative_player9': "",
        'alternative_player10': "",
        'url_player': ""
    },
    'PlayerFriendlyName': {
        'default_player_name': "",
        'alternative_player1_name': "",
        'alternative_player2_name': "",
        'alternative_player3_name': "",
        'alternative_player4_name': "",
        'alternative_player5_name': "",
        'alternative_player6_name': "",
        'alternative_player7_name': "",
        'alternative_player8_name': "",
        'alternative_player9_name': "",
        'alternative_player10_name': "",
        'url_player_name': ""
    },
    'DefaultApp': {
        'Image': ""
    },
    'Logging': {
        'use_socket_log': 'False',
        'log_level': '1',
        'logging_port': '19996'
    },
    'Database': {
        'url': 'sqlite:///{}'.format(DATABASE_PATH)
    }
}

DEFAULTS_HOTKEYS = {
    'Global': {
        'preferences': 'Ctrl+P',
        'hotkeys': 'F2',
        'quit': 'Ctrl+Q',
        'copy_all_urls': 'Ctrl+D',
        'refresh_feed': 'Ctrl+R',
        'refresh_feed_deep': 'Ctrl+T',
        'reload_subslist': 'Ctrl+L',
        'test_channels': "",
        'manual_dir_search': "",
        'manual_thumb_dl': "",
        'manual_db_grab': 'Ctrl+E',
        'download_video_by_url': 'Ctrl+O',
        'show_usage_history': 'Ctrl+H',
        'history_undo_action': 'Ctrl+Z'
    },
    'View': {
        'subfeed': 'Ctrl+1',
        'playback': 'Ctrl+2',
        'detailed_list': 'Ctrl+3',
        'download': 'Ctrl+4',
        'subscriptions': 'Ctrl+5',
        'tiled_list': 'Ctrl+9',
        'config': 'Ctrl+P'
    },
    'Subfeed': {
        'download': 'LeftButton',
        'dismiss': 'MidButton'
    },
    'Playback': {
        'prio_decrease': 'MidButton, Ctrl+LeftButton',
        'mark_watched': 'Alt+LeftButton',
        'play': 'MouseLeftButton',
        'ascending_sort_toggle': 'Ctrl+A',
        'by_channel_sort_toggle': 'Ctrl+B'
    }
}


def create_config_file(file_path, template: dict):
    """
    Creates a config file in file_path using the given template dict.
    :param file_path:
    :param template:
    :return:
    """
    cfg_parser = ConfigParser()

    if file_path == SAMPLE_PATH:
        # Special handling required for config.ini.sample
        for cfg_section in DEFAULTS:
            if cfg_section == 'Database':
                # Mask database path so it's not included in sample ini file
                modified_section = copy.deepcopy(DEFAULTS[cfg_section])
                modified_section['url'] = 'sqlite:///<path>/permanents.db'
                cfg_parser[cfg_section] = modified_section
            else:
                cfg_parser[cfg_section] = DEFAULTS[cfg_section]
    else:
        cfg_parser.read_dict(template)

    with open(file_path, 'w') as config_file:
        cfg_parser.write(config_file)


def read_config(section, option, literal_eval=True, custom_ini=None):
    """
    Reads a configuration file (INI format)
    :param section:
    :param option:
    :param literal_eval: eval config literally, instead of string
    :param custom_ini: if set, use given custom config
    :return:
    """
    defaults = DEFAULTS
    parser = default_parser
    # Support multiple configs
    if custom_ini is not None:
        # logger.debug("Reading custom config: {}".format(custom_ini))
        if custom_ini == "hotkeys":
            defaults = DEFAULTS_HOTKEYS
            parser = hotkeys_parser
        else:
            raise ValueError("Custom config '{}' is not defined in handler!!".format(custom_ini))

    if literal_eval:
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
    if _parser.has_section(section):
        return_options = _parser.options(section)
    else:
        # FIXME: check for correct custom_ini
        if custom_ini:
            return_options = DEFAULTS_HOTKEYS[section].keys()
        else:
            return_options = DEFAULTS[section].keys()

    return return_options


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
    Sets the given option's value
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


# Create sample config if none exists
if not os.path.exists(SAMPLE_PATH):
    create_config_file(SAMPLE_PATH, DEFAULTS)

# Create sample hotkeys config if none exists
if not os.path.exists(SAMPLE_HOTKEYS_PATH):
    create_config_file(SAMPLE_HOTKEYS_PATH, DEFAULTS_HOTKEYS)
