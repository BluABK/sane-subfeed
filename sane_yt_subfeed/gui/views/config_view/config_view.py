import os

# from PyQt5 import Qt
from PyQt5.QtCore import Qt  # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

from sane_yt_subfeed.config_handler import read_config, set_config, read_entire_config, get_sections, get_options
import sane_yt_subfeed.gui.views.config_view.checkbox as checkbox


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
        # deco_l = "███████████████████████ 【"
        # deco_r = "】 ███████████████████████"
        deco_l = "【"
        deco_r = "】"
        gui_section = QLabel('{}GUI{}'.format(deco_l, deco_r))
        launch_gui_opt = QLabel('Launch GUI?')
        launch_gui_val = QCheckBox("(Default: {})".format(str(read_config('Gui', 'launch_gui'))), self)
        launch_gui_val.setCheckState(2 if read_config('Gui', 'launch_gui') else 0)
        launch_gui_val.stateChanged.connect(checkbox.check_box_gui_launch_gui)
        hide_downloaded_vids_opt = QLabel('Hide downloaded videos from feed')
        hide_downloaded_vids_val = QCheckBox("(Default: {})".format(str(read_config('Gui', 'hide_downloaded'))), self)
        hide_downloaded_vids_val.setCheckState(2 if read_config('Gui', 'hide_downloaded') else 0)
        hide_downloaded_vids_val.stateChanged.connect(checkbox.check_box_gui_hide_downloaded)
        gridview_x_opt = QLabel('Grid view X')
        gridview_x_val = QLabel(str(read_config('Gui', 'grid_view_x')))
        gridview_y_opt = QLabel('Grid view Y')
        gridview_y_val = QLabel(str(read_config('Gui', 'grid_view_y')))

        # Section [Debug]
        section_debug = QLabel('{}Debug{}'.format(deco_l, deco_r))
        debug_opt = QLabel('Debug')
        debug_val = QCheckBox("(Default: {})".format(str(read_config('Debug', 'debug'))), self)
        debug_val.setCheckState(2 if read_config('Debug', 'debug') else 0)
        debug_val.stateChanged.connect(checkbox.check_box_debug_toggle)
        cache_subs_opt = QLabel('Cache subscriptions')
        cache_subs_val = QCheckBox("(Default: {})".format(str(read_config('Debug', 'cached_subs'))), self)
        cache_subs_val.setCheckState(2 if read_config('Debug', 'cached_subs') else 0)
        cache_subs_val.stateChanged.connect(checkbox.check_box_debug_cached_subs)
        start_with_cached_vids_opt = QLabel('Start with cached videos')
        start_with_cached_vids_val = QCheckBox(
            "(Default: {})".format(str(read_config('Debug', 'start_with_stored_videos'))), self)
        start_with_cached_vids_val.setCheckState(2 if read_config('Debug', 'start_with_stored_videos') else 0)
        start_with_cached_vids_val.stateChanged.connect(checkbox.check_box_debug_start_with_stored_videos)
        channel_limit_opt = QLabel('Channel limit')
        channel_limit_val = QLabel(str(read_config('Debug', 'channels_limit')))
        use_playlist_items_opt = QLabel('Use playlistItems')
        use_playlist_items_val = QCheckBox("(Default: {})".format(str(read_config('Debug', 'use_playlistItems'))), self)
        use_playlist_items_val.setCheckState(2 if read_config('Debug', 'use_playlistItems') else 0)
        use_playlist_items_val.stateChanged.connect(checkbox.check_box_debug_use_playlistitems)
        disable_tooltips_opt = QLabel('Disable tooltips')
        disable_tooltips_val = QCheckBox("(Default: {})".format(str(read_config('Debug', 'disable_tooltips'))), self)
        disable_tooltips_val.setCheckState(2 if read_config('Debug', 'disable_tooltips') else 0)
        disable_tooltips_val.stateChanged.connect(checkbox.check_box_debug_disable_tooltips)
        disable_tqdm_opt = QLabel('Disable tqdm (cli)')
        disable_tqdm_val = QCheckBox("(Default: {})".format(str(read_config('Debug', 'disable_tqdm'))), self)
        disable_tqdm_val.setCheckState(2 if read_config('Debug', 'disable_tqdm') else 0)
        disable_tqdm_val.stateChanged.connect(checkbox.check_box_debug_disable_tqdm)

        # Section [Requests]
        requests_section = QLabel('{}Requests{}'.format(deco_l, deco_r))
        use_tests_opt = QLabel('Use tests')
        use_tests_val = QCheckBox("(Default: {})".format(str(read_config('Requests', 'use_tests'))), self)
        use_tests_val.setCheckState(2 if read_config('Requests', 'use_tests') else 0)
        use_tests_val.stateChanged.connect(checkbox.check_box_requests_use_tests)
        missed_vid_limit_opt = QLabel('Missed video limit')
        missed_vid_limit_val = QLabel(str(read_config('Requests', 'miss_limit')))
        test_pages_opt = QLabel('Test pages')
        test_pages_val = QLabel(str(read_config('Requests', 'test_pages')))

        # Section [Thumbnails]
        thumbnails_section = QLabel('{}Thumbnails{}'.format(deco_l, deco_r))
        force_dl_best_thumb_opt = QLabel('Force download best quality, based on prioritised list')
        force_dl_best_thumb_val = QCheckBox(
            "(Default: {})".format(str(read_config('Thumbnails', 'force_download_best'))), self)
        force_dl_best_thumb_val.setCheckState(2 if read_config('Thumbnails', 'force_download_best') else 0)
        force_dl_best_thumb_val.stateChanged.connect(checkbox.check_box_thumbnails_force_download_best)
        force_dl_best_thumb_prio_1_opt = QLabel('1. Priority')
        force_dl_best_thumb_prio_1_val = QLabel(str(read_config('Thumbnails', '0')))
        force_dl_best_thumb_prio_2_opt = QLabel('2. Priority')
        force_dl_best_thumb_prio_2_val = QLabel(str(read_config('Thumbnails', '1')))
        force_dl_best_thumb_prio_3_opt = QLabel('3. Priority')
        force_dl_best_thumb_prio_3_val = QLabel(str(read_config('Thumbnails', '2')))
        force_dl_best_thumb_prio_4_opt = QLabel('4. Priority')
        force_dl_best_thumb_prio_4_val = QLabel(str(read_config('Thumbnails', '3')))
        force_dl_best_thumb_prio_5_opt = QLabel('5. Priority')
        force_dl_best_thumb_prio_5_val = QLabel(str(read_config('Thumbnails', '4')))

        # Section [Threading]
        threading_section = QLabel('{}Threading{}'.format(deco_l, deco_r))
        img_thread_limit_opt = QLabel('Image/thumbnail download thread limit')
        img_thread_limit_val = QLabel(str(read_config('Threading', 'img_threads')))

        section_offset = 0

        layout.addWidget(gui_section, (section_offset + 0), 0)
        section_offset += 1
        layout.addWidget(launch_gui_opt, (section_offset + 0), 0)
        layout.addWidget(launch_gui_val, (section_offset + 0), 1)
        layout.addWidget(hide_downloaded_vids_opt, (section_offset + 1), 0)
        layout.addWidget(hide_downloaded_vids_val, (section_offset + 1), 1)
        layout.addWidget(gridview_x_opt, (section_offset + 2), 0)
        layout.addWidget(gridview_x_val, (section_offset + 2), 1)
        layout.addWidget(gridview_y_opt, (section_offset + 3), 0)
        layout.addWidget(gridview_y_val, (section_offset + 3), 1)

        layout.addWidget(section_debug, (section_offset + 4), 0)
        section_offset += 1
        layout.addWidget(debug_opt, (section_offset + 4), 0)
        layout.addWidget(debug_val, (section_offset + 4), 1)
        layout.addWidget(cache_subs_opt, (section_offset + 5), 0)
        layout.addWidget(cache_subs_val, (section_offset + 5), 1)
        layout.addWidget(start_with_cached_vids_opt, (section_offset + 6), 0)
        layout.addWidget(start_with_cached_vids_val, (section_offset + 6), 1)
        layout.addWidget(channel_limit_opt, (section_offset + 7), 0)
        layout.addWidget(channel_limit_val, (section_offset + 7), 1)
        layout.addWidget(use_playlist_items_opt, (section_offset + 8), 0)
        layout.addWidget(use_playlist_items_val, (section_offset + 8), 1)
        layout.addWidget(disable_tooltips_opt, (section_offset + 9), 0)
        layout.addWidget(disable_tooltips_val, (section_offset + 9), 1)
        layout.addWidget(disable_tooltips_val, (section_offset + 9), 1)
        layout.addWidget(disable_tqdm_opt, (section_offset + 10), 0)
        layout.addWidget(disable_tqdm_val, (section_offset + 10), 1)

        layout.addWidget(requests_section, (section_offset + 11), 0)
        section_offset += 1
        layout.addWidget(use_tests_opt, (section_offset + 11), 0)
        layout.addWidget(use_tests_val, (section_offset + 11), 1)
        layout.addWidget(missed_vid_limit_opt, (section_offset + 12), 0)
        layout.addWidget(missed_vid_limit_val, (section_offset + 12), 1)
        layout.addWidget(test_pages_opt, (section_offset + 13), 0)
        layout.addWidget(test_pages_val, (section_offset + 13), 1)

        layout.addWidget(thumbnails_section, (section_offset + 14), 0)
        section_offset += 1
        layout.addWidget(force_dl_best_thumb_opt, (section_offset + 14), 0)
        layout.addWidget(force_dl_best_thumb_val, (section_offset + 14), 1)
        layout.addWidget(force_dl_best_thumb_prio_1_opt, (section_offset + 15), 0)
        layout.addWidget(force_dl_best_thumb_prio_1_val, (section_offset + 15), 1)
        layout.addWidget(force_dl_best_thumb_prio_2_opt, (section_offset + 16), 0)
        layout.addWidget(force_dl_best_thumb_prio_2_val, (section_offset + 16), 1)
        layout.addWidget(force_dl_best_thumb_prio_3_opt, (section_offset + 17), 0)
        layout.addWidget(force_dl_best_thumb_prio_3_val, (section_offset + 17), 1)
        layout.addWidget(force_dl_best_thumb_prio_4_opt, (section_offset + 18), 0)
        layout.addWidget(force_dl_best_thumb_prio_4_val, (section_offset + 18), 1)
        layout.addWidget(force_dl_best_thumb_prio_5_opt, (section_offset + 19), 0)
        layout.addWidget(force_dl_best_thumb_prio_5_val, (section_offset + 19), 1)

        layout.addWidget(threading_section, (section_offset + 20), 0)
        section_offset += 1
        layout.addWidget(img_thread_limit_opt, (section_offset + 20), 0)
        layout.addWidget(img_thread_limit_val, (section_offset + 20), 1)
