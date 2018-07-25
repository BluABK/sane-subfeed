from PyQt5.QtCore import Qt  # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

from sane_yt_subfeed.config_handler import read_config, set_config, read_entire_config, get_sections, get_options

thumb_qualities = ['maxres', 'standard', 'high', 'medium', 'default']   # FIXME: Get QComboBox to set strings not ints
tt_font_sizes = ['h1', 'h2', 'h3', 'h4', 'h5', 'p']


def gui_grid_view_x(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Gui', 'grid_view_x', str(number + 1))


def gui_grid_view_y(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Gui', 'grid_view_x', str(number + 1))


def gui_tile_pref_height(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Gui', 'tile_pref_height', str(number + 1))


def gui_tile_pref_width(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Gui', 'tile_pref_width', str(number + 1))


def gui_tooltip_picture_width(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Gui', 'tooltip_picture_width', str(number + 1))


def gui_tooltip_picture_height(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Gui', 'tooltip_picture_height', str(number + 1))


def gui_tooltip_picture_size(font_size):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Gui', 'tooltip_picture_size', str(tt_font_sizes[font_size]))


def debug_channels_limit(value):
    """
    Sets the integer value of the current setting
    disabled = -1
    :return:
    """
    if value == "Disabled":
        print("disabled")
        value = -1
    else:
        value -= 1
    set_config('Debug', 'channels_limit', str(value))


def requests_miss_limit(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Requests', 'miss_limit', str(number + 1))


def requests_test_pages(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Requests', 'test_pages', str(number + 1))


def thumbnails_priority_1(quality):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Thumbnails', '0', str(thumb_qualities[quality]))


def thumbnails_priority_2(quality):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Thumbnails', '1', str(thumb_qualities[quality]))


def thumbnails_priority_3(quality):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Thumbnails', '2', str(thumb_qualities[quality]))


def thumbnails_priority_4(quality):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Thumbnails', '3', str(thumb_qualities[quality]))


def thumbnails_priority_5(quality):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Thumbnails', '4', str(thumb_qualities[quality]))


def threading_img_threads(number):
    """
    Sets the integer value of the current setting
    :return:
    """
    set_config('Threading', 'img_threads', str(number + 1))
