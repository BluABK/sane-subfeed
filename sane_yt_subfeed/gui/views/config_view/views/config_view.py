# PyQt5
import sys

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator, QPaintEvent, QPainter

# Internal
from PyQt5.QtWidgets import QStyleOption, QStyle

from sane_yt_subfeed.handlers.config_handler import get_options, read_config, has_section
from sane_yt_subfeed.gui.views.config_view.config_item_types import THUMBNAIL_QUALITIES, TT_FONT_SIZES, \
    LEFT_MOUSE_ACTIONS, TILE_TITLE_FONT_WEIGHTS
from sane_yt_subfeed.gui.views.config_view.input_super import InputSuper
from sane_yt_subfeed.constants import HEXADECIMAL_COLOR_REGEX

STRFTIME_FORMAT_URL = "https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior"


class ConfigViewWidget(InputSuper):
    """
    Configuration widget
    """

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
        elif self.tab_id == 'Download' and read_config('Play', 'enabled'):
            self.add_config_tab_download()
        elif self.tab_id == 'Apps && Players':
            self.add_config_tab_apps()
        elif self.tab_id == "Time && Date":
            self.add_config_tab_datetime()
        elif self.tab_id == 'Logging':
            self.add_config_tab_logging()
        elif self.tab_id == 'Advanced':
            self.add_config_tab_advanced()

        self.init_ui()

    def paintEvent(self, paint_event: QPaintEvent):
        """
        Override painEvent in order to support stylesheets.
        :param paint_event:
        :return:
        """
        style_option = QStyleOption()
        style_option.initFrom(self)
        painter = QPainter(self)
        style = self.style()
        style.drawPrimitive(QStyle.PE_Widget, style_option, painter, self)

    def init_ui(self):
        """
        Initialize UI.
        :return:
        """
        self.logger.info("Initializing UI: ConfigViewWidget: {}".format(self.tab_id))

    def add_config_tab_gui(self):
        self.add_option_line_edit('Videos to load by default', 'Model', 'loaded_videos',
                                  cfg_validator=QIntValidator())
        self.add_option_checkbox('Grey background on old (1d+) videos', 'Gui', 'grey_old_videos')
        self.add_option_line_edit('Grid tile height (px)', 'Gui', 'tile_pref_height', cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid tile width (px)', 'Gui', 'tile_pref_width', cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid tile overlay height (%)', 'Gui', 'tile_overlay_height_pct',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid tile overlay width (%)', 'Gui', 'tile_overlay_width_pct',
                                  cfg_validator=QIntValidator())
        self.add_option_checkbox('Embed thumbnails in tooltips', 'Gui', 'tooltip_pictures')
        tooltip_thumb_disabled = not read_config('Gui', 'tooltip_pictures')
        self.add_option_line_edit('\tTooltip picture width', 'Gui', 'tooltip_picture_width',
                                  cfg_validator=QIntValidator(), disabled=tooltip_thumb_disabled)
        self.add_option_line_edit('\tTooltip picture height', 'Gui', 'tooltip_picture_height',
                                  cfg_validator=QIntValidator(), disabled=tooltip_thumb_disabled)
        self.add_option_combobox('\tTooltip picture font size', 'Gui', 'tooltip_picture_size',
                                 TT_FONT_SIZES, disabled=tooltip_thumb_disabled)
        self.add_option_checkbox('Keep Aspect Ratio on resized thumbnails', 'Gui', 'keep_thumb_ar', restart_check=False)
        self.add_option_checkbox('Auto copy to clipboard', 'Gui', 'enable_auto_copy_to_clipboard', restart_check=False)
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
        self.add_option_checkbox('Warn if video is SD quality', 'GridView', 'show_sd_warning', restart_check=False)
        self.add_option_checkbox('Show if video has captions available', 'GridView', 'show_has_captions',
                                 restart_check=False)
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
        self.add_option_fontpicker('Thumbnail overlay font', 'Fonts', 'video_thumbnail_overlay_font')
        self.add_option_fontpicker('Title font', 'Fonts', 'video_title_font')
        self.add_option_line_edit('Title elided text multiplier',
                                  'GridView', 'elided_text_modifier_title', cfg_validator=QDoubleValidator())
        self.add_option_line_edit('Title lines to display', 'GridView', 'tile_title_lines',
                                  cfg_validator=QIntValidator())
        self.add_option_info(None, None)  # Line spacer
        self.add_option_fontpicker('Channel font', 'Fonts', 'video_channel_font')
        self.add_option_line_edit('Channel elided text multiplier',
                                  'GridView', 'elided_text_modifier_channel', cfg_validator=QDoubleValidator())
        self.add_option_line_edit('Channel Title lines to display', 'GridView', 'tile_channel_lines',
                                  cfg_validator=QIntValidator())
        self.add_option_info(None, None)  # Line spacer
        self.add_option_fontpicker('Date font', 'Fonts', 'video_date_font')
        self.add_option_line_edit('Date elided text multiplier',
                                  'GridView', 'elided_text_modifier_date', cfg_validator=QDoubleValidator())
        self.add_option_line_edit('Date lines to display', 'GridView', 'tile_date_lines',
                                  cfg_validator=QIntValidator())
        self.add_option_info(None, None)  # Line spacer
        self.add_option_checkbox('Also add spacing between thumbnail and title',
                                 'GridView', 'add_thumbnail_spacer')
        self.add_option_line_edit('Line spacing for tile elements<br/>'
                                  '(tip: decrement this if you increment lines)', 'GridView', 'tile_line_spacing',
                                  QDoubleValidator())
        self.add_option_line_edit('Unicode line height offset (UTF > ASCII linebreaks)', 'GridView',
                                  'tile_unicode_line_height_offset', cfg_validator=QDoubleValidator())
        self.add_option_line_edit('Elided text UTF-8 weight modifier<br/>'
                                  '(Set this to 0 if using phantomstyle)', 'GridView',
                                  'elided_text_unicode_weight_modifier', cfg_validator=QDoubleValidator())
        self.add_option_info(None, None)  # Line spacer

        # Section [SubFeed]
        self.add_section('{}Subscription feed{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Show downloaded videos', 'SubFeed', 'show_downloaded')
        # FIXME: implement in hotkeys?
        self.add_option_combobox('Left click mouse action', 'SubFeed', 'left_mouse_action', LEFT_MOUSE_ACTIONS,
                                 restart_check=False)

        # Section [SubSort]
        self.add_section('{}Subscription feed (sorting){}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Sort by ascending date', 'SubSort', 'ascending_date')
        self.add_option_checkbox('Sort by channel', 'SubSort', 'by_channel')
        self.add_option_checkbox('Pin livestreams', 'SubSort', 'pin_live_broadcast_content', restart_check=False)

        # Section [DownloadView]
        if read_config('Play', 'enabled'):
            self.add_section('{}Downloads view{}'.format(self.deco_l, self.deco_r))
            self.add_option_line_edit('Download view tile height', 'DownloadView', 'download_tile_height',
                                      cfg_validator=QIntValidator())

        # Section [Play]
        if read_config('Play', 'enabled'):
            self.add_section('{}Playback feed{}'.format(self.deco_l, self.deco_r))
            self.add_option_line_edit('Default watch priority', 'Play', 'default_watch_prio',
                                      cfg_validator=QIntValidator(), restart_check=False)
            # Section [PlaySort]
            self.add_section('{}Playback feed (sorting){}'.format(self.deco_l, self.deco_r))
            self.add_option_checkbox('Sort by ascending date', 'PlaySort', 'ascending_date')
            self.add_option_checkbox('Sort by channel', 'PlaySort', 'by_channel')
        self.add_option_info_restart_required()

    def add_config_tab_debug(self):
        self.add_option_checkbox('Show unimplemented GUI elements', 'Debug', 'show_unimplemented_gui')
        self.add_option_checkbox('Display all Exceptions', 'Debug', 'display_all_exceptions', restart_check=False)
        self.add_option_info_restart_required()

    def add_config_tab_download(self):
        # Section [Youtube-dl]
        if 'youtube_dl' in sys.modules:
            self.add_option_checkbox('Use youtube-dl?', 'Youtube-dl', 'use_youtube_dl', restart_check=False)

            # Section [Youtube-dl_proxies]
            _counter = 1
            for proxy in get_options('Youtube-dl_proxies'):
                self.add_option_line_edit('Geoblock proxy #{}'.format(_counter), 'Youtube-dl_proxies', proxy,
                                          restart_check=False)
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
        self.add_option_checkbox('Prefer ffmpeg (over avconv)?', 'Postprocessing', 'prefer_ffmpeg', restart_check=False)
        self.add_option_line_edit('ffmpeg location', 'Postprocessing', 'ffmpeg_location', restart_check=False)
        self.add_option_checkbox('Embed metadata?', 'Postprocessing', 'embed_metadata', restart_check=False)
        if 'youtube_dl' not in sys.modules:
            self.add_option_info_restart_required()

        self.add_option_line_edit('YouTube video directory', 'Play', 'yt_file_path', restart_check=False)
        self.add_option_checkbox('Disable directory listener (inotify)', 'Play', 'disable_dir_listener')

    def add_config_tab_apps(self):
        self.add_section('{}Media Players{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Default Media Player', 'Player', 'default_player', restart_check=False)
        _counter = 1
        for alt_player in get_options('Player'):
            # if _counter == 1:  # Skip default player
            #     _counter += 1
            #     continue
            if "alternative_player" in alt_player:
                self.add_option_line_edit('Alternative Player #{}'.format(_counter), 'Player', alt_player,
                                          restart_check=False)
                _counter += 1

        self.add_section('{}Default Applications{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Default Web Browser<br/>'
                                  '(Uses system default if none specified)', 'Player', 'url_player',
                                  restart_check=False)
        self.add_option_line_edit('Image viewer', 'DefaultApp', 'Image', restart_check=False)

    def add_config_tab_datetime(self):
        self.add_section('{}Datetime{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Use ISO format on datetime', 'GridView', 'use_iso_datetime_format')
        self.add_option_line_edit('ISO format separator', 'GridView', 'iso_format_separator')
        self.add_option_line_edit('Custom Datetime format (<a href={}>strftime</a>):'.format(STRFTIME_FORMAT_URL),
                                  'GridView', 'custom_datetime_format')
        self.add_section('{}Timedelta{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Show timedelta instead of datetime', 'GridView', 'use_timedelta')
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

    def add_config_tab_logging(self):
        self.add_option_checkbox('Use socket instead of file', 'Logging', 'use_socket_log')
        self.add_option_line_edit('Log level', 'Logging', 'log_level', cfg_validator=QIntValidator())
        self.add_option_line_edit('Port', 'Logging', 'logging_port', cfg_validator=QIntValidator())
        self.add_option_info('Level\t Name', None)
        for level, value in self.logger.my_log_levels.items():
            self.add_option_info('{}\t{}'.format(value, level), None)
        self.add_option_info_restart_required()

    def add_config_tab_advanced(self):
        self.add_section('{}General{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Debug mode', 'Debug', 'debug',
                                 checked_actions=[self.config_view_tabs.add_tab,
                                                  self.root.respawn_menubar_and_toolbar],
                                 checked_kwargs=[{'tab': 'Debug'}, None],
                                 unchecked_actions=[self.config_view_tabs.del_tab,
                                                    self.root.respawn_menubar_and_toolbar],
                                 unchecked_kwargs=[{'tab': 'Debug'}, None])

        self.add_section('{}GUI{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Launch GUI', 'Gui', 'launch_gui', disabled=True)
        self.add_option_checkbox('Disable tooltips', 'Debug', 'disable_tooltips', restart_check=False)
        self.add_option_line_edit('Grid view X', 'Gui', 'grid_view_x', cfg_validator=QIntValidator())
        self.add_option_line_edit('Grid view Y', 'Gui', 'grid_view_y', cfg_validator=QIntValidator())
        self.add_option_line_edit('Duration overlay left padding', 'GridView', 'duration_right_padding',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Duration overlay bottom padding', 'GridView', 'duration_bottom_padding',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Captions overlay left padding', 'GridView', 'captions_left_padding',
                                  cfg_validator=QIntValidator())
        self.add_option_line_edit('Captions overlay bottom padding', 'GridView', 'captions_bottom_padding',
                                  cfg_validator=QIntValidator())

        self.add_section('{}Thumbnails{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Force download best quality, based on prioritised list',
                                 'Thumbnails', 'force_download_best', restart_check=False)
        self.add_option_combobox('1. Priority', 'Thumbnails', '0', THUMBNAIL_QUALITIES, restart_check=False)
        self.add_option_combobox('2. Priority', 'Thumbnails', '1', THUMBNAIL_QUALITIES, restart_check=False)
        self.add_option_combobox('3. Priority', 'Thumbnails', '2', THUMBNAIL_QUALITIES, restart_check=False)
        self.add_option_combobox('4. Priority', 'Thumbnails', '3', THUMBNAIL_QUALITIES, restart_check=False)
        self.add_option_combobox('5. Priority', 'Thumbnails', '4', THUMBNAIL_QUALITIES, restart_check=False)

        self.add_section('{}Threading{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Image/thumbnail download thread limit', 'Threading', 'img_threads',
                                  cfg_validator=QIntValidator(), restart_check=False)
        self.add_option_line_edit('Max failed operation retry attempts', 'Threading', 'retry_attempts',
                                  cfg_validator=QIntValidator(), restart_check=False)
        self.add_option_line_edit('Failed operation retry delay (in seconds)', 'Threading', 'retry_delay',
                                  cfg_validator=QDoubleValidator(), restart_check=False)

        self.add_section('{}YouTube requests{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Channel limit (-1 is unlimited)', 'Debug', 'channels_limit',
                                  cfg_validator=QIntValidator(), restart_check=False)
        self.add_option_checkbox('Use list() instead of search()', 'Debug', 'use_playlistitems', restart_check=False)
        self.add_option_checkbox('Use tests', 'Requests', 'use_tests', restart_check=False)
        self.add_option_line_edit('Missed video limit', 'Requests', 'miss_limit',
                                  cfg_validator=QIntValidator(), restart_check=False)
        self.add_option_line_edit('Test pages', 'Requests', 'test_pages',
                                  cfg_validator=QIntValidator(), restart_check=False)
        self.add_option_line_edit('Additional list pages', 'Requests', 'extra_list_pages',
                                  cfg_validator=QIntValidator(), restart_check=False)
        self.add_option_line_edit('Deep search API quota limit per request (in K)', 'Requests',
                                  'deep_search_quota_k',
                                  cfg_validator=QIntValidator(), restart_check=False)
        self.add_option_line_edit('Filter videos older than (days)', 'Requests', 'filter_videos_days_old',
                                  cfg_validator=QIntValidator(), restart_check=False)

        self.add_section('{}Cache{}'.format(self.deco_l, self.deco_r))
        self.add_option_checkbox('Cache subscriptions', 'Debug', 'cached_subs')
        self.add_option_checkbox('Start with cached videos', 'Debug', 'start_with_stored_videos')

        self.add_section('{}Database{}'.format(self.deco_l, self.deco_r))
        self.add_option_line_edit('Database URL', 'Database', 'url')

        self.add_option_info_restart_required()
