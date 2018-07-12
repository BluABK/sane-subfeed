import os

# from PyQt5 import Qt
from PyQt5.QtCore import Qt     # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

from sane_yt_subfeed.config_handler import read_config, set_config, read_entire_config, get_sections, get_options


class ConfigView(QWidget):
    """
    Configuration widget
    """

    def __init__(self, parent, clipboard, status_bar):
        """
        A GUI Widget that reads and sets config.ini settings
        :param parent:
        :param clipboard:
        :param status_bar:
        """
        super(ConfigView, self).__init__(parent)
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.init_ui()

    def init_ui(self):
        """
        Initialize UI
        :return:
        """
        layout = QGridLayout()
        self.setLayout(layout)

        # Section [Gui]
        deco_l = "███████████████████████ 【"
        deco_r = "】 ███████████████████████"
        section_label_0 = QLabel('{}GUI{}'.format(deco_l, deco_r))
        option_label_0 = QLabel('Launch GUI?')
        # value_label_0 = QLabel(str(read_config('Gui', 'launch_gui')))
        value_label_0 = QCheckBox("(Default: {})".format(str(read_config('Gui', 'launch_gui'))), self)
        value_label_0.setCheckState(2 if read_config('Gui', 'launch_gui') else 1)
        value_label_0.stateChanged.connect(self.check_box_gui_launch_gui)
        option_label_1 = QLabel('Hide downloaded videos from feed')
        value_label_1 = QLabel(str(read_config('Gui', 'hide_downloaded')))
        option_label_2 = QLabel('Grid view X')
        value_label_2 = QLabel(str(read_config('Gui', 'grid_view_x')))
        option_label_3 = QLabel('Grid view Y')
        value_label_3 = QLabel(str(read_config('Gui', 'grid_view_y')))

        # Section [Debug]
        section_label_1 = QLabel('{}Debug{}'.format(deco_l, deco_r))
        option_label_4 = QLabel('Debug')
        value_label_4 = QLabel(str(read_config('Debug', 'debug')))
        option_label_5 = QLabel('Cache subscriptions')
        value_label_5 = QLabel(str(read_config('Debug', 'cached_subs')))
        option_label_6 = QLabel('Start with cached videos')
        value_label_6 = QLabel(str(read_config('Debug', 'start_with_stored_videos')))
        option_label_7 = QLabel('Channel limit')
        value_label_7 = QLabel(str(read_config('Debug', 'channels_limit')))
        option_label_8 = QLabel('Use playlistItems')
        value_label_8 = QLabel(str(read_config('Debug', 'use_playlistItems')))
        option_label_9 = QLabel('Disable tooltips')
        value_label_9 = QLabel(str(read_config('Debug', 'disable_tooltips')))
        option_label_10 = QLabel('Disable tqdm (cli)')
        value_label_10 = QLabel(str(read_config('Debug', 'disable_tqdm')))

        # Section [Requests]
        section_label_2 = QLabel('{}Requests{}'.format(deco_l, deco_r))
        option_label_11 = QLabel('Use tests')
        value_label_11 = QLabel(str(read_config('Requests', 'use_tests')))
        option_label_12 = QLabel('Missed video limit')
        value_label_12 = QLabel(str(read_config('Requests', 'miss_limit')))
        option_label_13 = QLabel('Test pages')
        value_label_13 = QLabel(str(read_config('Requests', 'test_pages')))

        # Section [Thumbnails]
        section_label_3 = QLabel('{}Thumbnails{}'.format(deco_l, deco_r))
        option_label_14 = QLabel('Force download best quality, based on prioritised list')
        value_label_14 = QLabel(str(read_config('Thumbnails', 'force_download_best')))
        option_label_15 = QLabel('1. Priority')
        value_label_15 = QLabel(str(read_config('Thumbnails', '0')))
        option_label_16 = QLabel('2. Priority')
        value_label_16 = QLabel(str(read_config('Thumbnails', '1')))
        option_label_17 = QLabel('3. Priority')
        value_label_17 = QLabel(str(read_config('Thumbnails', '2')))
        option_label_18 = QLabel('4. Priority')
        value_label_18 = QLabel(str(read_config('Thumbnails', '3')))
        option_label_19 = QLabel('5. Priority')
        value_label_19 = QLabel(str(read_config('Thumbnails', '4')))

        # Section [Threading]
        section_label_4 = QLabel('{}Threading{}'.format(deco_l, deco_r))
        option_label_20 = QLabel('Image/thumbnail download thread limit')
        value_label_20 = QLabel(str(read_config('Threading', 'img_threads')))

        section_offset = 0

        layout.addWidget(section_label_0, (section_offset + 0), 0)
        section_offset += 1
        layout.addWidget(option_label_0, (section_offset + 0), 0)
        layout.addWidget(value_label_0, (section_offset + 0), 1)
        layout.addWidget(option_label_1, (section_offset + 1), 0)
        layout.addWidget(value_label_1, (section_offset + 1), 1)
        layout.addWidget(option_label_2, (section_offset + 2), 0)
        layout.addWidget(value_label_2, (section_offset + 2), 1)
        layout.addWidget(option_label_3, (section_offset + 3), 0)
        layout.addWidget(value_label_3, (section_offset + 3), 1)

        layout.addWidget(section_label_1, (section_offset + 4), 0)
        section_offset += 1
        layout.addWidget(option_label_4, (section_offset + 4), 0)
        layout.addWidget(value_label_4, (section_offset + 4), 1)
        layout.addWidget(option_label_5, (section_offset + 5), 0)
        layout.addWidget(value_label_5, (section_offset + 5), 1)
        layout.addWidget(option_label_6, (section_offset + 6), 0)
        layout.addWidget(value_label_6, (section_offset + 6), 1)
        layout.addWidget(option_label_7, (section_offset + 7), 0)
        layout.addWidget(value_label_7, (section_offset + 7), 1)
        layout.addWidget(option_label_8, (section_offset + 8), 0)
        layout.addWidget(value_label_8, (section_offset + 8), 1)
        layout.addWidget(option_label_9, (section_offset + 9), 0)
        layout.addWidget(value_label_9, (section_offset + 9), 1)
        layout.addWidget(value_label_9, (section_offset + 9), 1)
        layout.addWidget(option_label_10, (section_offset + 10), 0)
        layout.addWidget(value_label_10, (section_offset + 10), 1)

        layout.addWidget(section_label_2, (section_offset + 11), 0)
        section_offset += 1
        layout.addWidget(option_label_11, (section_offset + 11), 0)
        layout.addWidget(value_label_11, (section_offset + 11), 1)
        layout.addWidget(option_label_12, (section_offset + 12), 0)
        layout.addWidget(value_label_12, (section_offset + 12), 1)
        layout.addWidget(option_label_13, (section_offset + 13), 0)
        layout.addWidget(value_label_13, (section_offset + 13), 1)

        layout.addWidget(section_label_3, (section_offset + 14), 0)
        section_offset += 1
        layout.addWidget(option_label_14, (section_offset + 14), 0)
        layout.addWidget(value_label_14, (section_offset + 14), 1)
        layout.addWidget(option_label_15, (section_offset + 15), 0)
        layout.addWidget(value_label_15, (section_offset + 15), 1)
        layout.addWidget(option_label_16, (section_offset + 16), 0)
        layout.addWidget(value_label_16, (section_offset + 16), 1)
        layout.addWidget(option_label_17, (section_offset + 17), 0)
        layout.addWidget(value_label_17, (section_offset + 17), 1)
        layout.addWidget(option_label_18, (section_offset + 18), 0)
        layout.addWidget(value_label_18, (section_offset + 18), 1)
        layout.addWidget(option_label_19, (section_offset + 19), 0)
        layout.addWidget(value_label_19, (section_offset + 19), 1)

        layout.addWidget(section_label_4, (section_offset + 20), 0)
        section_offset += 1
        layout.addWidget(option_label_20, (section_offset + 20), 0)
        layout.addWidget(value_label_20, (section_offset + 20), 1)

    @staticmethod
    def check_box_section_template(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('', '', '')
        else:
            set_config('', '', '')

    @staticmethod
    def check_box_gui_launch_gui(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('Gui', 'launch_gui', 'True')
        else:
            set_config('Gui', 'launch_gui', 'False')

    @staticmethod
    def check_box_gui_hide_downloaded(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('Gui', 'hide_downloaded', 'True')
        else:
            set_config('Gui', 'hide_downloaded', 'False')

    @staticmethod
    def check_box_debug_start_with_stored_videos(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('Debug', 'start_with_stored_videos', 'True')
        else:
            set_config('Debug', 'start_with_stored_videos', 'False')

    @staticmethod
    def check_box_debug_use_playlistitems(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('Debug', 'use_playlistitems', 'True')
        else:
            set_config('Debug', 'use_playlistitems', 'False')

    @staticmethod
    def disable_tooltips(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('Debug', 'disable_tooltips', 'True')
        else:
            set_config('Debug', 'disable_tooltips', 'False')

    @staticmethod
    def check_box_debug_disable_tqdm(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('Debug', 'disable_tqdm', 'True')
        else:
            set_config('Debug', 'disable_tqdm', 'False')

    @staticmethod
    def check_box_requests_use_tests(state):
        """
        Toggles the given setting between True and False
        :param state: 0=unchecked, 1=tristate?, 2=checked
        :return:
        """
        if state == Qt.Checked:
            set_config('Requests', 'use_tests', 'True')
        else:
            set_config('Requests', 'use_tests', 'False')
