from PyQt5.QtCore import Qt     # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

from sane_yt_subfeed.config_handler import read_config, set_config, read_entire_config, get_sections, get_options


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