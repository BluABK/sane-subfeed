from PyQt5.QtCore import Qt  # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

from sane_yt_subfeed.config_handler import read_config, set_config, read_entire_config, get_sections, get_options

# ######################################################################## #
# ################################# [GUI] ################################ #
# ######################################################################## #


def gui_launch_gui(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Gui', 'launch_gui', 'True')
    else:
        set_config('Gui', 'launch_gui', 'False')


def gui_hide_downloaded(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Gui', 'hide_downloaded', 'True')
    else:
        set_config('Gui', 'hide_downloaded', 'False')


def gui_grey_old_videos(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Gui', 'grey_old_videos', 'True')
    else:
        set_config('Gui', 'grey_old_videos', 'False')


def gui_enable_grid_resize(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Gui', 'enable_grid_resize', 'True')
    else:
        set_config('Gui', 'enable_grid_resize', 'False')


def gui_tooltip_pictures(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Gui', 'tooltip_pictures', 'True')
    else:
        set_config('Gui', 'tooltip_pictures', 'False')


def gui_keep_thumb_ar(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Gui', 'keep_thumb_ar', 'True')
    else:
        set_config('Gui', 'keep_thumb_ar', 'False')


def gui_enable_auto_copy_to_clipboard(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Gui', 'enable_auto_copy_to_clipboard', 'True')
    else:
        set_config('Gui', 'enable_auto_copy_to_clipboard', 'False')

# ######################################################################## #
# ################################ [Debug] ############################### #
# ######################################################################## #


def debug_toggle(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'debug', 'True')
    else:
        set_config('Debug', 'debug', 'False')


def debug_cached_subs(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'cached_subs', 'True')
    else:
        set_config('Debug', 'cached_subs', 'False')


def debug_start_with_stored_videos(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'start_with_stored_videos', 'True')
    else:
        set_config('Debug', 'start_with_stored_videos', 'False')


def debug_use_playlistitems(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'use_playlistitems', 'True')
    else:
        set_config('Debug', 'use_playlistitems', 'False')


def debug_disable_tooltips(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'disable_tooltips', 'True')
    else:
        set_config('Debug', 'disable_tooltips', 'False')


def debug_disable_tqdm(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'disable_tqdm', 'True')
    else:
        set_config('Debug', 'disable_tqdm', 'False')


def debug_show_grab_method(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'show_grab_method', 'True')
    else:
        set_config('Debug', 'show_grab_method', 'False')


def debug_log_search_method(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'log_search', 'True')
    else:
        set_config('Debug', 'log_search', 'False')


def debug_log_list_method(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'log_list', 'True')
    else:
        set_config('Debug', 'log_list', 'False')


def debug_show_unimplemented_gui(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Debug', 'show_unimplemented_gui', 'True')
    else:
        set_config('Debug', 'show_unimplemented_gui', 'False')

# ######################################################################## #
# ############################## [Requests] ############################## #
# ######################################################################## #


def requests_use_tests(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Requests', 'use_tests', 'True')
    else:
        set_config('Requests', 'use_tests', 'False')

# ######################################################################## #
# ############################# [Thumbnails] ############################# #
# ######################################################################## #


def thumbnails_force_download_best(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Thumbnails', 'force_download_best', 'True')
    else:
        set_config('Thumbnails', 'force_download_best', 'False')


# ######################################################################## #
# ################################ [Play] ################################ #
# ######################################################################## #

def play_disable_dir_listener(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Play', 'disable_dir_listener', 'True')
    else:
        set_config('Play', 'disable_dir_listener', 'False')


def play_use_url_as_path(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Play', 'use_url_as_path', 'True')
    else:
        set_config('Play', 'use_url_as_path', 'False')


# ######################################################################## #
# ############################# [Youtube-dl] ############################# #
# ######################################################################## #

def ytdl_use_youtube_dl(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Youtube-dl', 'use_youtube_dl', 'True')
    else:
        set_config('Youtube-dl', 'use_youtube_dl', 'False')


# ######################################################################## #
# ############################### [Logger] ############################### #
# ######################################################################## #

def logger_use_socket(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Logging', 'use_socket_log', 'True')
    else:
        set_config('Logging', 'use_socket_log', 'False')


# ######################################################################## #
# ############################### [Toolbar] ############################### #
# ######################################################################## #

def toolbar_show_download_video_field(state):
    """
    Toggles the given setting between True and False
    :param state: 0=unchecked, 1=tristate?, 2=checked
    :return:
    """
    if state == Qt.Checked:
        set_config('Toolbar', 'show_download_video_field', 'True')
    else:
        set_config('Toolbar', 'show_download_video_field', 'False')