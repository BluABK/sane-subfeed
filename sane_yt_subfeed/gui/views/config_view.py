import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, qApp, QMenu, QGridLayout, QLabel, QVBoxLayout, QLineEdit, QApplication, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter

from sane_yt_subfeed.config_handler import read_config, read_entire_config, get_sections, get_options


class ConfigView(QWidget):

    def __init__(self, parent, clipboard, status_bar):
        super(ConfigView, self).__init__(parent)
        # self.config_file = None
        self.clipboard = clipboard
        self.status_bar = status_bar
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        option_layout = QHBoxLayout()
        self.setLayout(layout)

        config = read_entire_config()
        print(config)
        items = []
        for section in config:
            for i in range(len(config[section])):
                items.append(option_layout)

        positions = [(i, j) for i in range(len(items)) for j in range(2)]

        counter = 0
        # for section, options_list in config:        # {[section: [options]}
        #     for options_dict in options_list:       # [options]
        #         for option, value in options_dict:  # {option: value}
        config = {}
        # for section in get_sections():
        #     # print("[{}]".format(section))
        #     config[section] = []
        #     section_option = {}
        #     for option in get_options(section):
        #         value = read_config(section, option)
        #         section_option[option] = value
        #         config[section].append(section_option)

                # for position, option_layout in zip(positions, items):
                #     if option == '':  # FIXME: Replace with None for making a blank slot, and also implement better.
                #         continue
                #     option_label = QLabel(option)
                #     option_layout.addWidget(option_label)
                #     layout.addWidget(option_layout, *position)
                #     option_layout.addWidget(QLabel(str(value)))



        # Section [Gui]
        deco_l = "███████████████████████ 【"
        deco_r = "】 ███████████████████████"
        section_label_0 = QLabel('{}GUI{}'.format(deco_l, deco_r))
        option_label_0 = QLabel('Launch GUI?')
        value_label_0 = QLabel(str(read_config('Gui', 'launch_gui')))
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
        layout.addWidget(option_label_1, (section_offset + 1), 0)
        layout.addWidget(option_label_2, (section_offset + 2), 0)
        layout.addWidget(option_label_3, (section_offset + 3), 0)

        layout.addWidget(section_label_1, (section_offset + 4), 0)
        section_offset += 1
        layout.addWidget(option_label_4, (section_offset + 4), 0)
        layout.addWidget(option_label_5, (section_offset + 5), 0)
        layout.addWidget(option_label_6, (section_offset + 6), 0)
        layout.addWidget(option_label_7, (section_offset + 7), 0)
        layout.addWidget(option_label_8, (section_offset + 8), 0)
        layout.addWidget(option_label_9, (section_offset + 9), 0)
        layout.addWidget(option_label_10, (section_offset + 10), 0)

        layout.addWidget(section_label_2, (section_offset + 11), 0)
        section_offset += 1
        layout.addWidget(option_label_11, (section_offset + 11), 0)
        layout.addWidget(option_label_12, (section_offset + 12), 0)
        layout.addWidget(option_label_13, (section_offset + 13), 0)

        layout.addWidget(section_label_3, (section_offset + 14), 0)
        section_offset += 1
        layout.addWidget(option_label_14, (section_offset + 14), 0)
        layout.addWidget(option_label_15, (section_offset + 15), 0)
        layout.addWidget(option_label_16, (section_offset + 16), 0)
        layout.addWidget(option_label_17, (section_offset + 17), 0)
        layout.addWidget(option_label_18, (section_offset + 18), 0)
        layout.addWidget(option_label_19, (section_offset + 19), 0)

        layout.addWidget(section_label_4, (section_offset + 20), 0)
        section_offset += 1
        layout.addWidget(option_label_20, (section_offset + 20), 0)

        # # Section [Gui]
        # layout.addWidget(QLabel('launch_gui'), (0, 0)) # = True
        # layout.addWidget(QLabel('hide_downloaded'), (1, 0)) # = True
        # layout.addWidget(QLabel('grid_view'), (2, 0)) # _x = 5
        # layout.addWidget(QLabel('grid_view'), (3, 0)) # _y = 4
        #
        # # Section [Debug]
        # layout.addWidget(QLabel('debug'), (4, 0)) #  = False
        # layout.addWidget(QLabel('cached_subs'), (5, 0)) #  = True
        # layout.addWidget(QLabel('start_with_stored_videos'), (6, 0)) #  = False
        # layout.addWidget(QLabel('channels_limit'), (7, 0)) #  = -1
        # layout.addWidget(QLabel('use_playlistItems'), (8, 0)) #  = True
        # layout.addWidget(QLabel('disable_tooltips'), (9, 0)) #  = False
        # layout.addWidget(QLabel('disable_tqdm'), (10, 0)) #  = True
        #
        # # Section [Requests]
        # layout.addWidget(QLabel('use_tests'), (11, 0)) #  = False
        # layout.addWidget(QLabel('miss_limit'), (12, 0)) #  = 10
        # layout.addWidget(QLabel('test_pages'), (13, 0)) #  = 2
        #
        # # Section [Thumbnails]
        # layout.addWidget(QLabel('force_download_best'), (14, 0)) #  = True
        # layout.addWidget(QLabel('0'), (15, 0)) #  = maxres
        # layout.addWidget(QLabel('1'), (16, 0)) #  = standard
        # layout.addWidget(QLabel('2'), (17, 0)) #  = high
        # layout.addWidget(QLabel('3'), (18, 0)) #  = medium
        # layout.addWidget(QLabel('4'), (19, 0)) #  = default
        #
        # # Section [Threading]
        # layout.addWidget(QLabel('img_threads'), (20, 0)) #   = 200

