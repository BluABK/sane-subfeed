# PyQt5
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QComboBox

# Internal
from sane_yt_subfeed.config_handler import DEFAULTS, get_size, get_options
# import sane_yt_subfeed.gui.views.config_view.checkbox as checkbox
from sane_yt_subfeed.gui.views.config_view.config_item_types import THUMBNAIL_QUALITIES, TT_FONT_SIZES
from sane_yt_subfeed.gui.views.config_view.config_items import checkbox, combobox
from sane_yt_subfeed.gui.views.config_view.config_items.checkbox import GenericConfigCheckBox
from sane_yt_subfeed.gui.views.config_view.config_items.combobox import GenericConfigComboBox
from sane_yt_subfeed.gui.views.config_view.config_items.line_edit import GenericLineEdit
from sane_yt_subfeed.gui.views.config_view.input_super import InputSuper
from sane_yt_subfeed.log_handler import create_logger


class ConfigViewWidget(InputSuper):
    """
    Configuration widget
    """
    deco_l = "【"
    deco_r = "】"

    def __init__(self, parent, root):
        """
        A GUI Widget that reads and sets config.ini settings
        :param parent:
        :param clipboard:
        :param status_bar:
        """
        super().__init__(parent, root)
        self.populate_options()
        self.init_ui()

    def init_ui(self):
        """
        Initialize UI
        :return:
        """
        self.logger.info("Initializing UI")
        mismatch = get_size() - self.offset
        if mismatch != 0:
            self.logger.warning("ConfigView is missing {} entries!".format(mismatch))

    def populate_options(self):
        """
        Populate the layout with sections, options and (editable) values
        :return:
        """

        # Section [Gui]
        self.add_section('{}GUI{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Launch GUI', 'Gui', 'launch_gui')
        self.add_option_checkbox('Hide downloaded videos from feed', 'Gui',
                                 'hide_downloaded')
        self.add_option_line_edit('Grid view X', 'Gui', 'grid_view_x', cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid view Y', 'Gui', 'grid_view_y', cfg_validator=QIntValidator())
        self.add_option_checkbox('Grey background on old (1d+) videos', 'Gui', 'grey_old_videos')
        self.add_option_line_edit('\tGrid tile height (px)', 'Gui', 'tile_pref_height', cfg_validator=QIntValidator())
        self.add_option_line_edit('\tGrid tile width (px)', 'Gui', 'tile_pref_width', cfg_validator=QIntValidator())
        self.add_option_checkbox('Embed thumbnails in tooltips', 'Gui', 'tooltip_pictures')
        self.add_option_line_edit('\tTooltip picture width', 'Gui', 'tooltip_picture_width',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('\tTooltip picture height', 'Gui', 'tooltip_picture_height',
                                  cfg_validator=QIntValidator())
        self.add_option_combobox('\tTooltip picture font size', 'Gui', 'tooltip_picture_size', TT_FONT_SIZES)
        self.add_option_checkbox('Keep Aspect Ratop on resized thumbnails', 'Gui', 'keep_thumb_ar')
        self.add_option_checkbox('Auto copy to clipboard', 'Gui', 'enable_auto_copy_to_clipboard')

        # Section [GridView]
        self.add_section('{}View: GridView{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Show watched videos', 'GridView', 'show_watched')
        self.add_option_checkbox('Show dismissed videos', 'GridView', 'show_dismissed')

        # Section [Debug]
        self.add_section('{}Debug{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Debug prints', 'Debug', 'debug')
        self.add_option_checkbox('Cache subscriptions', 'Debug', 'cached_subs')
        self.add_option_checkbox('Start with cached videos', 'Debug', 'start_with_stored_videos')
        self.add_option_line_edit('Channel limit', 'Debug', 'channels_limit', cfg_validator=QIntValidator())
        self.add_option_checkbox('Use playlistItems', 'Debug', 'use_playlistitems')
        self.add_option_checkbox('Disable tooltips', 'Debug', 'disable_tooltips')
        self.add_option_checkbox('Disable tqdm (cli)', 'Debug', 'disable_tqdm')
        self.add_option_checkbox('Show channel grab methods', 'Debug', 'show_grab_method')
        self.add_option_checkbox('Log all YouTube API responses: search()', 'Debug', 'log_search')
        self.add_option_checkbox('Log all YouTube API responses: list()', 'Debug', 'log_list')
        self.add_option_line_edit('\t Haystack needle ', 'Debug', 'log_needle')
        self.add_option_checkbox('Show unimplemented GUI elements', 'Debug', 'show_unimplemented_gui')

        # Section [Model]
        self.add_section('{}Model{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Videos to load by default', 'Model', 'loaded_videos', cfg_validator=QIntValidator())

        # Section [Requests]
        self.add_section('{}Requests{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Use tests', 'Requests', 'use_tests')
        self.add_option_line_edit('Missed video limit', 'Requests', 'miss_limit', cfg_validator=QIntValidator())
        self.add_option_line_edit('Test pages', 'Requests', 'test_pages', cfg_validator=QIntValidator())
        self.add_option_line_edit('Additional list pages', 'Requests', 'extra_list_pages',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Deep search API quota limit per request (in K)', 'Requests', 'deep_search_quota_k',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Filter videos older than (days)', 'Requests', 'filter_videos_days_old',
                                  cfg_validator=QIntValidator())

        # Section [Thumbnails]
        self.add_section('{}Thumbnails{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Force download best quality, based on prioritised list',
                                 'Thumbnails', 'force_download_best')
        self.add_option_combobox('1. Priority', 'Thumbnails', '0', THUMBNAIL_QUALITIES)
        self.add_option_combobox('2. Priority', 'Thumbnails', '1', THUMBNAIL_QUALITIES)
        self.add_option_combobox('3. Priority', 'Thumbnails', '2', THUMBNAIL_QUALITIES)
        self.add_option_combobox('4. Priority', 'Thumbnails', '3', THUMBNAIL_QUALITIES)
        self.add_option_combobox('5. Priority', 'Thumbnails', '4', THUMBNAIL_QUALITIES)

        # Section [Threading]
        self.add_section('{}Threading{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Image/thumbnail download thread limit', 'Threading', 'img_threads',
                                  cfg_validator=QIntValidator())

        # Section [Play]
        self.add_section('{}View: Playback{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('YouTube video directory', 'Play', 'yt_file_path')
        self.add_option_checkbox('Disable directory listener (inotify)', 'Play', 'disable_dir_listener')
        self.add_option_checkbox('Use URL as path', 'Play', 'use_url_as_path')
        self.add_option_line_edit('Default watch priority', 'Play', 'default_watch_prio', cfg_validator=QIntValidator())

        # Section [Youtube-dl]
        self.add_section('{}Downloading / youtube-dl{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Use youtube-dl?', 'Youtube-dl', 'use_youtube_dl')

        # Section [Youtube-dl_proxies]
        self.add_section('{}Download (geoblock failover) proxy{}'.format(self.deco_l, self.deco_r))
        _counter = 1
        for proxy in get_options('Youtube-dl_proxies'):
            self.add_option_line_edit('Proxy #{}'.format(_counter), 'Youtube-dl_proxies', proxy)
            _counter += 1

        # Section [Player]
        self.add_section('{}Media player{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Default Player', 'Player', 'default_player')
        self.add_option_line_edit('Url Player', 'Player', 'url_player')
        _counter = 1
        for alt_player in get_options('Player'):
            # if _counter == 1:  # Skip default player
            #     _counter += 1
            #     continue
            if "alternative_player" in alt_player:
                self.add_option_line_edit('Alternative Player #{}'.format(_counter), 'Player', alt_player)
                _counter += 1

        # Section [Logging]
        self.add_section('{}Logging{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Use socket instead of file', 'Logging', 'use_socket_log')
        self.add_option_line_edit('Log level', 'Logging', 'log_level', cfg_validator=QIntValidator())
        self.add_option_line_edit('Port', 'Logging', 'logging_port', cfg_validator=QIntValidator())

        # Section [Toolbar]
        self.add_section('{}Toolbar{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Show on-demand download video field?', 'Toolbar', 'show_download_video_field')
