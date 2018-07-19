# PyQt5
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

# Internal
from sane_yt_subfeed.config_handler import read_config, defaults
import sane_yt_subfeed.gui.views.config_view.checkbox as checkbox


class ConfigView(QWidget):
    """
    Configuration widget
    """
    offset = 0
    layout = None
    deco_l = "【"
    deco_r = "】"

    # Options tied to listeners or similar
    launch_gui = None
    hide_downloaded_vids = None
    debug_toggle = None
    cache_subs = None
    start_with_cached_vids = None
    use_playlist_items = None
    disable_tooltips = None
    disable_tqdm = None
    use_tests = None
    force_dl_best_thumb = None

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
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.populate_options()

    def add_section(self, name):
        """
        Add a section to the ConfigView layout and increment grid offset.
        :return:
        """
        self.layout.addWidget(QLabel(name), self.offset, 0)
        self.offset += 1

    def add_option_checkbox(self, option_name, current_value, value_listener):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param current_value:
        :param value_listener:
        :param option_name:
        :return:
        """
        option = QLabel(option_name)
        value = QCheckBox("(Default: {})".format(str(current_value)), self)  # FIXME: use default dict
        value.setCheckState(2 if current_value else 0)
        value.stateChanged.connect(value_listener)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_inactive(self, option_name, current_value):
        """
        Add an option w/ UNEDITABLE value to the ConfigView layout and increment the grid offset.
        :param current_value:
        :param option_name:
        :return:
        """
        option = QLabel(option_name)
        value = QLabel(str(current_value))
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def populate_options(self):
        """
        Populate the layout with sections, options and (editable) values
        :return:
        """
        # Section [Gui]
        self.add_section('{}GUI{}'.format(self.deco_l, self.deco_r))
        self.launch_gui = self.add_option_checkbox('Launch GUI?', read_config('Gui', 'launch_gui'),
                                                   checkbox.gui_launch_gui)
        self.hide_downloaded_vids = self.add_option_checkbox('Hide downloaded videos from feed',
                                                             read_config('Gui', 'hide_downloaded'),
                                                             checkbox.gui_hide_downloaded)
        self.add_option_inactive('Grid view X', read_config('Gui', 'grid_view_x'))
        self.add_option_inactive('Grid view Y', read_config('Gui', 'grid_view_y'))

        # Section [Debug]
        self.add_section('{}Debug{}'.format(self.deco_l, self.deco_r))
        self.debug_toggle = self.add_option_checkbox('Debug', read_config('Debug', 'debug'), checkbox.debug_toggle)
        self.cache_subs = self.add_option_checkbox('Cache subscriptions', read_config('Debug', 'cached_subs'),
                                                   checkbox.debug_cached_subs)
        self.start_with_cached_vids = self.add_option_checkbox('Start with cached videos',
                                                               read_config('Debug', 'start_with_stored_videos'),
                                                               checkbox.debug_start_with_stored_videos)
        self.add_option_inactive('Channel limit', read_config('Debug', 'channels_limit'))
        self.use_playlist_items = self.add_option_checkbox('Use playlistItems',
                                                           read_config('Debug', 'use_playlistItems'),
                                                           checkbox.debug_use_playlistitems)
        self.disable_tooltips = self.add_option_checkbox('Disable tooltips', read_config('Debug', 'disable_tooltips'),
                                                         checkbox.debug_disable_tooltips)
        self.disable_tqdm = self.add_option_checkbox('Disable tqdm (cli)', read_config('Debug', 'disable_tqdm'),
                                                     checkbox.debug_disable_tqdm)

        # Section [Requests]
        self.add_section('{}Requests{}'.format(self.deco_l, self.deco_r))
        self.use_tests = self.add_option_checkbox('Use tests', read_config('Requests', 'use_tests'),
                                                  checkbox.requests_use_tests)
        self.add_option_inactive('Missed video limit', read_config('Requests', 'miss_limit'))
        self.add_option_inactive('Test pages', read_config('Requests', 'test_pages'))

        # Section [Thumbnails]
        self.add_section('{}Thumbnails{}'.format(self.deco_l, self.deco_r))
        self.force_dl_best_thumb = self.add_option_checkbox('Force download best quality, based on prioritised list',
                                                            read_config('Thumbnails', 'force_download_best'),
                                                            checkbox.thumbnails_force_download_best)
        self.add_option_inactive('1. Priority', read_config('Thumbnails', '0'))
        self.add_option_inactive('2. Priority', read_config('Thumbnails', '1'))
        self.add_option_inactive('3. Priority', read_config('Thumbnails', '2'))
        self.add_option_inactive('4. Priority', read_config('Thumbnails', '3'))
        self.add_option_inactive('5. Priority', read_config('Thumbnails', '4'))

        # Section [Threading]
        self.add_section('{}Threading{}'.format(self.deco_l, self.deco_r))
        self.add_option_inactive('Image/thumbnail download thread limit', read_config('Threading', 'img_threads'))
