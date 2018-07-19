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

    def add_option_checkbox(self, description, cfg_section, cfg_option, value_listener):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param cfg_option:
        :param cfg_section:
        :param value_listener:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = QCheckBox("(Default: {})".format(str(defaults[cfg_section][cfg_option])), self)
        value.setCheckState(2 if read_config(cfg_section, cfg_option) else 0)
        value.stateChanged.connect(value_listener)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_inactive(self, description, cfg_section, cfg_option):
        """
        Add an option w/ UNEDITABLE value to the ConfigView layout and increment the grid offset.
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = QLabel(str(defaults[cfg_section][cfg_option]))
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
        self.launch_gui = self.add_option_checkbox('Launch GUI?', 'Gui', 'launch_gui', checkbox.gui_launch_gui)
        self.hide_downloaded_vids = self.add_option_checkbox('Hide downloaded videos from feed', 'Gui',
                                                             'hide_downloaded', checkbox.gui_hide_downloaded)
        self.add_option_inactive('Grid view X', 'Gui', 'grid_view_x')
        self.add_option_inactive('Grid view Y', 'Gui', 'grid_view_y')

        # Section [Debug]
        self.add_section('{}Debug{}'.format(self.deco_l, self.deco_r))
        self.debug_toggle = self.add_option_checkbox('Debug', 'Debug', 'debug', checkbox.debug_toggle)
        self.cache_subs = self.add_option_checkbox('Cache subscriptions', 'Debug', 'cached_subs',
                                                   checkbox.debug_cached_subs)
        self.start_with_cached_vids = self.add_option_checkbox('Start with cached videos', 'Debug',
                                                               'start_with_stored_videos',
                                                               checkbox.debug_start_with_stored_videos)
        self.add_option_inactive('Channel limit', 'Debug', 'channels_limit')
        self.use_playlist_items = self.add_option_checkbox('Use playlistItems', 'Debug', 'use_playlistitems',
                                                           checkbox.debug_use_playlistitems)
        self.disable_tooltips = self.add_option_checkbox('Disable tooltips', 'Debug', 'disable_tooltips',
                                                         checkbox.debug_disable_tooltips)
        self.disable_tqdm = self.add_option_checkbox('Disable tqdm (cli)', 'Debug', 'disable_tqdm',
                                                     checkbox.debug_disable_tqdm)

        # Section [Requests]
        self.add_section('{}Requests{}'.format(self.deco_l, self.deco_r))
        self.use_tests = self.add_option_checkbox('Use tests', 'Requests', 'use_tests', checkbox.requests_use_tests)
        self.add_option_inactive('Missed video limit', 'Requests', 'miss_limit')
        self.add_option_inactive('Test pages', 'Requests', 'test_pages')

        # Section [Thumbnails]
        self.add_section('{}Thumbnails{}'.format(self.deco_l, self.deco_r))
        self.force_dl_best_thumb = self.add_option_checkbox('Force download best quality, based on prioritised list',
                                                            'Thumbnails', 'force_download_best',
                                                            checkbox.thumbnails_force_download_best)
        self.add_option_inactive('1. Priority', 'Thumbnails', '0')
        self.add_option_inactive('2. Priority', 'Thumbnails', '1')
        self.add_option_inactive('3. Priority', 'Thumbnails', '2')
        self.add_option_inactive('4. Priority', 'Thumbnails', '3')
        self.add_option_inactive('5. Priority', 'Thumbnails', '4')

        # Section [Threading]
        self.add_section('{}Threading{}'.format(self.deco_l, self.deco_r))
        self.add_option_inactive('Image/thumbnail download thread limit', 'Threading', 'img_threads')
