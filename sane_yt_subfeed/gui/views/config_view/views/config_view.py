# PyQt5
import sys

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator

# Internal
from sane_yt_subfeed.config_handler import get_options, read_config, has_section
from sane_yt_subfeed.gui.views.config_view.config_item_types import THUMBNAIL_QUALITIES, TT_FONT_SIZES, \
    LEFT_MOUSE_ACTIONS
from sane_yt_subfeed.gui.views.config_view.input_super import InputSuper
from sane_yt_subfeed.constants import HEXADECIMAL_COLOR_REGEX


class ConfigViewWidget(InputSuper):
    """
    Configuration widget
    """
    # deco_l = "【"
    # deco_r = "】"
    # deco_l = "┣━━━━━━━━━━━━━━━━━━━━━━━━ "
    # deco_r = " ━━━━━━━━━━━━━━━━━━━━━━━━┣"

    deco_l = ""
    deco_r = ""

    def __init__(self, config_view_tabs, parent, root, tab_id):
        """
        A GUI Widget that reads and sets config.ini settings
        :param parent:
        """
        super().__init__(parent, root)
        self.root = root
        self.parent = parent
        self.tab_id = tab_id
        self.config_view_tabs = config_view_tabs

        # Populate options for the given tab
        if self.tab_id == 'GUI':
            self.add_config_tab_gui()
        elif self.tab_id == 'Views':
            self.add_config_tab_views()
        elif self.tab_id == 'Debug' and read_config('Debug', 'debug'):
            self.add_config_tab_debug()
        elif self.tab_id == 'Model':
            self.add_config_tab_model()
        elif self.tab_id == 'Requests':
            self.add_config_tab_requests()
        elif self.tab_id == 'Thumbnails':
            self.add_config_tab_thumbnails()
        elif self.tab_id == 'Threading':
            self.add_config_tab_threading()
        elif self.tab_id == 'Download' and read_config('Play', 'enabled'):
            self.add_config_tab_download()
        elif self.tab_id == 'Media player':
            self.add_config_tab_mediaplayer()
        elif self.tab_id == 'Default Application':
            self.add_config_tab_default_apps()
        elif self.tab_id == 'Logging':
            self.add_config_tab_logging()
        elif self.tab_id == 'Advanced':
            self.add_config_tab_advanced()

        self.init_ui()

    def init_ui(self):
        """
        Initialize UI.
        :return:
        """
        self.logger.info("Initializing UI: ConfigViewWidget: {}".format(self.tab_id))

    def add_config_tab_gui(self):
        self.add_option_line_edit('Grid view X', 'Gui', 'grid_view_x', cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid view Y', 'Gui', 'grid_view_y', cfg_validator=QIntValidator())
        self.add_option_checkbox('Grey background on old (1d+) videos', 'Gui', 'grey_old_videos')
        self.add_option_line_edit('Grid tile height (px)', 'Gui', 'tile_pref_height', cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid tile width (px)', 'Gui', 'tile_pref_width', cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid tile overlay height (%)', 'Gui', 'tile_overlay_height_pct',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid tile overlay width (%)', 'Gui', 'tile_overlay_width_pct',
                                  cfg_validator=QIntValidator())
        self.add_option_checkbox('Embed thumbnails in tooltips', 'Gui', 'tooltip_pictures')
        self.add_option_line_edit('\tTooltip picture width', 'Gui', 'tooltip_picture_width',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('\tTooltip picture height', 'Gui', 'tooltip_picture_height',
                                  cfg_validator=QIntValidator())
        self.add_option_combobox('\tTooltip picture font size', 'Gui', 'tooltip_picture_size', TT_FONT_SIZES)
        self.add_option_checkbox('Keep Aspect Ratop on resized thumbnails', 'Gui', 'keep_thumb_ar')
        self.add_option_checkbox('Auto copy to clipboard', 'Gui', 'enable_auto_copy_to_clipboard')
        self.add_section('{}Theme{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Set custom background color hexadecimal <br/>'
                                  '(only works in default theme. Ex: #ffffff for white bg)',
                                  'Gui', 'bgcolor',
                                  cfg_validator=QRegExpValidator(QRegExp(HEXADECIMAL_COLOR_REGEX)))
        self.add_option_button('Clear bgcolor', 'Clears the background color setting ', 'Gui', 'bgcolor',
                               tooltip='(required due to validator shenanigans)', clear=True)
        self.add_option_checkbox('Use darkmode icon set', 'Gui', 'darkmode_icons')
        self.add_option_line_edit('Toolbar icon size modifier (Useful on High DPI displays)',
                                  'Gui', 'toolbar_icon_size_modifier', actions=[self.root.update_toolbar_size,
                                                                                self.root.respawn_menubar_and_toolbar])
        self.add_option_info_restart_required()

    def add_config_tab_views(self):
        # Section [GridView]
        self.add_section('{}Grid Views{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Show watched videos', 'GridView', 'show_watched')
        self.add_option_checkbox('Show dismissed videos', 'GridView', 'show_dismissed')
        self.add_option_checkbox('Enable Playback view (and download support)', 'Play', 'enabled',
                                 checked_actions=[self.config_view_tabs.add_tab,
                                                  self.root.respawn_menubar_and_toolbar,
                                                  self.root.add_central_widget_playback,
                                                  self.root.add_central_widget_download,
                                                  self.root.setup_views],
                                 checked_kwargs=[{'tab': 'Download'}, None, None, None, None],
                                 unchecked_actions=[self.config_view_tabs.del_tab,
                                                    self.root.respawn_menubar_and_toolbar,
                                                    self.root.del_central_widget_playback,
                                                    self.root.del_central_widget_download,
                                                    self.root.setup_views],
                                 unchecked_kwargs=[{'tab': 'Download'}, None, None, None, None])
        self.add_option_line_edit('Elided channel title text modifier (title-width * modifier)',
                                  'GridView', 'elided_text_modifier_channel', cfg_validator=QDoubleValidator())
        self.add_option_line_edit('Elided video title text modifier (title-width * modifier)',
                                  'GridView', 'elided_text_modifier_title', cfg_validator=QDoubleValidator())
        self.add_option_line_edit('Elided date text modifier (title-width * modifier)',
                                  'GridView', 'elided_text_modifier_date', cfg_validator=QDoubleValidator())
        self.add_option_line_edit('Title pixel size modifier (title-height * modifier)',
                                  'GridView', 'title_tile_pixel_size', cfg_validator=QDoubleValidator())

        self.add_option_line_edit('Date format for: videos uploaded'
                                  ' less than a day ago', 'GridView', 'timedelta_format')
        self.add_option_line_edit('Date format for: videos uploaded'
                                  ' a day ago', 'GridView', 'timedelta_format_days')
        self.add_option_line_edit('Date format for: videos uploaded'
                                  ' a month ago', 'GridView', 'timedelta_format_months')
        self.add_option_line_edit('Date format for: videos uploaded'
                                  ' a year ago', 'GridView', 'timedelta_format_years')
        self.add_option_line_edit('Date format for: videos uploaded'
                                  ' a decade ago', 'GridView', 'timedelta_format_decades')

        self.add_option_info('$decadesdecades', 'Decades as a zero-padded decimal number.')
        self.add_option_info('$decades', 'Decades as a decimal number.')
        self.add_option_info('$ydyd', '<u>Y</u>ears<u>d</u>elta as a zero-padded decimal number.')
        self.add_option_info('$yd', '<u>Y</u>ears<u>d</u>elta as a decimal number.')
        self.add_option_info('$mm', 'Months as a zero-padded decimal number.')
        self.add_option_info('$m', 'Months as a decimal number.')
        self.add_option_info('$dd', 'Days of the month as a zero-padded decimal number.')
        self.add_option_info('$d', 'Days of the month as a decimal number.')
        self.add_option_info('$HH', 'Hours (24-hour clock) as a zero-padded decimal number.')
        self.add_option_info('$H', 'Hours (24-hour clock) as a decimal number.')
        self.add_option_info('$MM', 'Minutes as a zero-padded decimal number.')
        self.add_option_info('$M', 'Minutes as a decimal number.')
        self.add_option_info('$SS', 'Seconds as a zero-padded decimal number.')
        self.add_option_info('$S', 'Seconds as a decimal number.')
        self.add_option_info('$f', 'Microseconds as a decimal number, zero-padded on the left.')
        self.add_option_info('$%', 'A literal \'%\' character.')
        self.add_option_info('', '')
        self.add_option_info('Valid delimters:', '$, ${}')

        # Section [SubFeed]
        self.add_section('{}Subscription feed{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Show downloaded videos', 'SubFeed', 'show_downloaded')
        # FIXME: implement in hotkeys?
        self.add_option_combobox('Left click mouse action', 'SubFeed', 'left_mouse_action', LEFT_MOUSE_ACTIONS)

        # Section [SubSort]
        self.add_section('{}Subscription feed (sorting){}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Sort by ascending date', 'SubSort', 'ascending_date')
        self.add_option_checkbox('Sort by channel', 'SubSort', 'by_channel')
        self.add_option_checkbox('Pin livestreams', 'SubSort', 'pin_live_broadcast_content')

        # Section [DownloadView]
        if read_config('Play', 'enabled'):
            self.add_section('{}Downloads view{}'.format(self.deco_l, self.deco_r))
            self.add_option_line_edit('Download view tile height', 'DownloadView', 'download_tile_height',
                                      cfg_validator=QIntValidator())

        # Section [Play]
        if read_config('Play', 'enabled'):
            self.add_section('{}Playback feed{}'.format(self.deco_l, self.deco_r))
            self.add_option_line_edit('YouTube video directory', 'Play', 'yt_file_path')
            self.add_option_checkbox('Disable directory listener (inotify)', 'Play', 'disable_dir_listener')
            self.add_option_checkbox('Use URL as path', 'Play', 'use_url_as_path')
            self.add_option_line_edit('Default watch priority', 'Play', 'default_watch_prio',
                                      cfg_validator=QIntValidator())
            # Section [PlaySort]
            self.add_section('{}Playback feed (sorting){}'.format(self.deco_l, self.deco_r))
            self.add_option_checkbox('Sort by ascending date', 'PlaySort', 'ascending_date')
            self.add_option_checkbox('Sort by channel', 'PlaySort', 'by_channel')
        self.add_option_info_restart_required()

    def add_config_tab_debug(self):
        self.add_option_checkbox('Cache subscriptions', 'Debug', 'cached_subs')
        self.add_option_checkbox('Start with cached videos', 'Debug', 'start_with_stored_videos')
        self.add_option_line_edit('Channel limit', 'Debug', 'channels_limit', cfg_validator=QIntValidator())
        self.add_option_checkbox('Use playlistItems', 'Debug', 'use_playlistitems')
        self.add_option_checkbox('Disable tooltips', 'Debug', 'disable_tooltips')
        self.add_option_checkbox('Show channel grab methods', 'Debug', 'show_grab_method')
        self.add_option_checkbox('Show unimplemented GUI elements', 'Debug', 'show_unimplemented_gui')
        self.add_option_checkbox('Display all Exceptions', 'Debug', 'display_all_exceptions')
        self.add_option_info_restart_required()

    def add_config_tab_model(self):
        self.add_option_line_edit('Videos to load by default', 'Model', 'loaded_videos',
                                  cfg_validator=QIntValidator())
        self.add_option_info_restart_required()

    def add_config_tab_requests(self):
        self.add_option_checkbox('Use tests', 'Requests', 'use_tests')
        self.add_option_line_edit('Missed video limit', 'Requests', 'miss_limit', cfg_validator=QIntValidator())
        self.add_option_line_edit('Test pages', 'Requests', 'test_pages', cfg_validator=QIntValidator())
        self.add_option_line_edit('Additional list pages', 'Requests', 'extra_list_pages',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Deep search API quota limit per request (in K)', 'Requests',
                                  'deep_search_quota_k',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Filter videos older than (days)', 'Requests', 'filter_videos_days_old',
                                  cfg_validator=QIntValidator())
        self.add_option_info_restart_required()

    def add_config_tab_thumbnails(self):
        self.add_option_checkbox('Force download best quality, based on prioritised list',
                                 'Thumbnails', 'force_download_best')
        self.add_option_combobox('1. Priority', 'Thumbnails', '0', THUMBNAIL_QUALITIES)
        self.add_option_combobox('2. Priority', 'Thumbnails', '1', THUMBNAIL_QUALITIES)
        self.add_option_combobox('3. Priority', 'Thumbnails', '2', THUMBNAIL_QUALITIES)
        self.add_option_combobox('4. Priority', 'Thumbnails', '3', THUMBNAIL_QUALITIES)
        self.add_option_combobox('5. Priority', 'Thumbnails', '4', THUMBNAIL_QUALITIES)
        self.add_option_info_restart_required()

    def add_config_tab_threading(self):
        self.add_option_line_edit('Image/thumbnail download thread limit', 'Threading', 'img_threads',
                                  cfg_validator=QIntValidator())
        self.add_option_info_restart_required()

    def add_config_tab_download(self):
        # Section [Youtube-dl]
        if 'youtube_dl' in sys.modules:
            self.add_option_checkbox('Use youtube-dl?', 'Youtube-dl', 'use_youtube_dl')

            # Section [Youtube-dl_proxies]
            _counter = 1
            for proxy in get_options('Youtube-dl_proxies'):
                self.add_option_line_edit('Geoblock proxy #{}'.format(_counter), 'Youtube-dl_proxies', proxy)
                _counter += 1
        else:
            self.add_option_checkbox('Use youtube-dl?<br/>'
                                     '<b><font color=#EF6262>MODULE UNAVAILABLE! (Is it installed?)</font></b>',
                                     'Youtube-dl', 'use_youtube_dl', disabled=True)

        # Section [Youtube-dl_opts]
        if has_section('Youtube-dl_opts') and 'youtube_dl' in sys.modules:
            if len(get_options('Youtube-dl_opts')) > 0:
                self.add_section('Youtube-DL options overrides (Config file only)')
                for option in get_options('Youtube-dl_opts'):
                    value = read_config('Youtube-dl_opts', option)
                    self.add_option_info("{}: ".format(option), "{}".format(value))

        self.add_section('Postprocessing')
        self.add_option_checkbox('Prefer ffmpeg?', 'Postprocessing', 'prefer_ffmpeg')
        self.add_option_line_edit('ffmpeg location', 'Postprocessing', 'ffmpeg_location')
        self.add_option_checkbox('Embed metadata?', 'Postprocessing', 'embed_metadata')
        self.add_option_info_restart_required()

    def add_config_tab_mediaplayer(self):
        # Section [Player]
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
        self.add_option_info_restart_required()

    def add_config_tab_default_apps(self):
        self.add_option_line_edit('Image viewer', 'DefaultApp', 'Image')
        self.add_option_info_restart_required()

    def add_config_tab_logging(self):
        self.add_option_checkbox('Use socket instead of file', 'Logging', 'use_socket_log')
        self.add_option_info('Value\t Level', None)
        self.add_option_info('50\t CRITICAL', None)
        self.add_option_info('40\t ERROR', None)
        self.add_option_info('30\t WARNING', None)
        self.add_option_info('20\t INFO', None)
        self.add_option_info('10\t DEBUG', None)
        self.add_option_info('5\t SPAM (Custom level)', None)
        self.add_option_info('1\t All of the above', None)
        self.add_option_info('0\t NOT SET', None)
        self.add_option_line_edit('Log level', 'Logging', 'log_level', cfg_validator=QIntValidator())
        self.add_option_line_edit('Port', 'Logging', 'logging_port', cfg_validator=QIntValidator())
        self.add_option_info_restart_required()

    def add_config_tab_advanced(self):
        self.add_option_checkbox('Launch GUI', 'Gui', 'launch_gui', disabled=True)
        self.add_option_checkbox('Debug mode', 'Debug', 'debug',
                                 checked_actions=[self.config_view_tabs.add_tab,
                                                  self.root.respawn_menubar_and_toolbar],
                                 checked_kwargs=[{'tab': 'Debug'}, None],
                                 unchecked_actions=[self.config_view_tabs.del_tab,
                                                    self.root.respawn_menubar_and_toolbar],
                                 unchecked_kwargs=[{'tab': 'Debug'}, None])
        self.add_option_info_restart_required()
