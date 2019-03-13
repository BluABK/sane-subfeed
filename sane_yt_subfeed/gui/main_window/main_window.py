# !/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

import copy
import os
import traceback
from PyQt5.QtCore import QFile, QTextStream, QRegExp
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QStackedWidget, QStyleFactory
from subprocess import check_output

# Project internal libs
# from sane_yt_subfeed import debug_functions
from sane_yt_subfeed.absolute_paths import ICONS_PATH, VERSION_PATH
from sane_yt_subfeed.config_handler import read_config, set_config
from sane_yt_subfeed.controller.listeners.listeners import LISTENER_SIGNAL_NORMAL_REFRESH, LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.controller.static_controller_vars import SUBFEED_VIEW_ID, PLAYBACK_VIEW_ID
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.dialogs.sane_confirmation_dialog import SaneConfirmationDialog
from sane_yt_subfeed.gui.dialogs.sane_input_dialog import SaneInputDialog
from sane_yt_subfeed.gui.dialogs.sane_text_view_dialog import SaneTextViewDialog
from sane_yt_subfeed.gui.exception_handler.sane_exception_handler import SaneExceptionHandler
from sane_yt_subfeed.gui.history.sane_history import SaneHistory
from sane_yt_subfeed.gui.main_window.db_state import DbStateIcon
from sane_yt_subfeed.gui.main_window.toolbar import Toolbar
from sane_yt_subfeed.gui.main_window.toolbar_action import SaneToolBarAction
from sane_yt_subfeed.gui.themes import themes
from sane_yt_subfeed.gui.themes.themes import THEMES_LIST, QSTYLES_AVAILABLE
from sane_yt_subfeed.gui.views.about_view.about_view import AboutView
from sane_yt_subfeed.gui.views.config_view.config_view_tabs import ConfigViewTabs
from sane_yt_subfeed.gui.views.config_view.config_window import ConfigWindow
from sane_yt_subfeed.gui.views.config_view.views.hotkeys_view import HotkeysViewWidget
from sane_yt_subfeed.gui.views.detailed_list_view.subfeed.list_detailed_view import SubfeedDetailedListView
from sane_yt_subfeed.gui.views.detailed_list_view.subscriptions.subscriptions_detailed_list_view import \
    SubscriptionsDetailedListView
from sane_yt_subfeed.gui.views.download_view.dl_scroll_area import DownloadScrollArea
from sane_yt_subfeed.gui.views.grid_view.grid_scroll_area import GridScrollArea
from sane_yt_subfeed.gui.views.grid_view.playback.playback_grid_view import PlaybackGridView
from sane_yt_subfeed.gui.views.grid_view.subfeed.subfeed_grid_view import SubfeedGridView
from sane_yt_subfeed.gui.views.tiled_list_view.subfeed.subfeed_tiled_list_view import SubfeedTiledListView
from sane_yt_subfeed.history_handler import get_plaintext_history
from sane_yt_subfeed.log_handler import create_logger

# Constants
HOTKEYS_EVAL = False
HOTKEYS_INI = 'hotkeys'
YOUTUBE_URL_REGEX = QRegExp('(http[s]?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/[^ ]+')
YOUTUBE_URL_REGEX.setCaseSensitivity(False)
QMAINWINDOW_TITLE = 'Sane Subscription Feed'
QMAINWINDOW_ICON = 'yubbtubbz-padding.ico'
SUBFEED_VIEW_ICON_LIGHT = 'grid.png'
SUBFEED_VIEW_ICON_DARK = 'grid_darkmode.png'
SUBFEED_VIEW_ICON = SUBFEED_VIEW_ICON_LIGHT
SUBFEED_TILED_LIST_VIEW_ICON_LIGHT = 'tiled_list.png'
SUBFEED_TILED_LIST_VIEW_ICON_DARK = 'tiled_list_darkmode.png'
SUBFEED_TILED_LIST_VIEW_ICON = SUBFEED_TILED_LIST_VIEW_ICON_LIGHT
PLAYBACK_VIEW_ICON_LIGHT = 'play_view_basic.png'
PLAYBACK_VIEW_ICON_DARK = 'play_view_basic_darkmode.png'
PLAYBACK_VIEW_ICON = PLAYBACK_VIEW_ICON_LIGHT
DETAILED_LIST_VIEW_ICON_LIGHT = 'table.png'
DETAILED_LIST_VIEW_ICON_DARK = 'table_darkmode.png'
DETAILED_LIST_VIEW_ICON = DETAILED_LIST_VIEW_ICON_LIGHT
DOWNLOAD_VIEW_ICON_LIGHT = 'download_view.png'
DOWNLOAD_VIEW_ICON_DARK = 'download_view_darkmode.png'
DOWNLOAD_VIEW_ICON = DOWNLOAD_VIEW_ICON_LIGHT
SUBS_LIST_VIEW_ICON = 'subs.png'
CONFIG_ICON_LIGHT = 'config.png'
CONFIG_ICON_DARK = 'config_darkmode.png'
CONFIG_ICON = CONFIG_ICON_LIGHT
HOTKEYS_ICON = 'hotkeys.png'
COPY_ALL_URLS_ICON = 'copy.png'
REFRESH_SUBFEED_ICON_LIGHT = 'refresh.png'
REFRESH_SUBFEED_ICON_DARK = 'refresh_darkmode.png'
REFRESH_SUBFEED_ICON = REFRESH_SUBFEED_ICON_LIGHT
REFRESH_SUBFEED_DEEP_ICON_LIGHT = 'refresh.png'
REFRESH_SUBFEED_DEEP_ICON_DARK = 'refresh_darkmode.png'
REFRESH_SUBFEED_DEEP_ICON = REFRESH_SUBFEED_DEEP_ICON_LIGHT
RELOAD_SUBS_LIST_ICON = 'refresh_subs.png'
RERUN_TEST_ICON = 'rerun_test.png'
MANUAL_DIR_SEARCH_ICON = 'folder_refresh.png'
MANUAL_THUMBS_DOWNLOAD_ICON = 'folder_refresh.png'
DATABASE_ICON = 'database.png'
SORT_BY_ASC_DATE_ICON = 'database.png'
SORT_BY_CHANNEL_ICON = 'database.png'
UNDO_ICON_LIGHT = 'refresh.png'
UNDO_ICON_DARK = 'refresh_darkmode.png'
UNDO_ICON = UNDO_ICON_LIGHT
ABOUT_ICON = 'about.png'

QMAINWINDOW_DIMENSIONS = [770, 700]


class MainWindow(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, app: QApplication, main_model: MainModel, dimensions=None, position=None):
        super().__init__()
        self.logger = create_logger(__name__)
        self.app = app
        self.main_model = main_model
        self.history = SaneHistory(self)

        # Create the Exception Handler
        self.exceptionHandler = SaneExceptionHandler(self)

        # Set the exception hook to be wrapped by the Exception Handler
        sys.excepthook = self.exceptionHandler.handler

        self.themes_list = THEMES_LIST
        self.bgcolor = read_config('Gui', 'bgcolor', literal_eval=False)
        self.darkmode = read_config('Gui', 'darkmode_icons')

        self.clipboard = QApplication.clipboard()
        self.status_bar = self.statusBar()

        self.position = position
        if dimensions:
            self.dimensions = dimensions
        else:
            self.dimensions = QMAINWINDOW_DIMENSIONS

        # Declare Views
        self.central_widget = None
        self.current_view = None
        self.subfeed_grid_view = None
        self.playback_grid_view = None
        self.subscriptions_view = None
        self.download_view = None
        self.config_view = None
        self.hotkeys_view = None
        self.list_detailed_view = None
        self.list_tiled_view = None
        self.about_view = None

        # Declare theming
        self.current_theme = None
        self.current_theme_idx = 0
        self.hotkey_ctrl_down = False

        # Declare MainWindow things
        self.views = {}
        self.menubar = None
        self.menus = {}
        self.toolbar = None
        self.toolbar_items = {}

        # Initialize UI
        self.init_ui()

    def determine_icons(self):
        """
        Determine which icons to use.

        Current use is to switch between darkmode and lightmode icons where applicable.
        :return:
        """
        # FIXME: Create a iconpack system instead of setting darkmode applicable icons explicitly light or dark
        global SUBFEED_VIEW_ICON, SUBFEED_TILED_LIST_VIEW_ICON, PLAYBACK_VIEW_ICON, DETAILED_LIST_VIEW_ICON
        global DOWNLOAD_VIEW_ICON, CONFIG_ICON, REFRESH_SUBFEED_ICON, REFRESH_SUBFEED_DEEP_ICON, UNDO_ICON

        if self.darkmode:
            SUBFEED_VIEW_ICON = SUBFEED_VIEW_ICON_DARK
            SUBFEED_TILED_LIST_VIEW_ICON = SUBFEED_TILED_LIST_VIEW_ICON_DARK
            PLAYBACK_VIEW_ICON = PLAYBACK_VIEW_ICON_DARK
            DETAILED_LIST_VIEW_ICON = DETAILED_LIST_VIEW_ICON_DARK
            DOWNLOAD_VIEW_ICON = DOWNLOAD_VIEW_ICON_DARK
            CONFIG_ICON = CONFIG_ICON_DARK
            REFRESH_SUBFEED_ICON = REFRESH_SUBFEED_ICON_DARK
            REFRESH_SUBFEED_DEEP_ICON = REFRESH_SUBFEED_DEEP_ICON_DARK
            UNDO_ICON = UNDO_ICON_DARK
        else:
            SUBFEED_VIEW_ICON = SUBFEED_VIEW_ICON_LIGHT
            SUBFEED_TILED_LIST_VIEW_ICON = SUBFEED_TILED_LIST_VIEW_ICON_LIGHT
            PLAYBACK_VIEW_ICON = PLAYBACK_VIEW_ICON_LIGHT
            DETAILED_LIST_VIEW_ICON = DETAILED_LIST_VIEW_ICON_LIGHT
            DOWNLOAD_VIEW_ICON = DOWNLOAD_VIEW_ICON_LIGHT
            CONFIG_ICON = CONFIG_ICON_LIGHT
            REFRESH_SUBFEED_ICON = REFRESH_SUBFEED_ICON_LIGHT
            REFRESH_SUBFEED_DEEP_ICON = REFRESH_SUBFEED_DEEP_ICON_LIGHT
            UNDO_ICON = UNDO_ICON_LIGHT

    def init_ui(self):
        self.logger.info("Initializing UI: MainWindow")

        self.determine_icons()
        # Setup the views
        self.setup_views()

        # Set the (last used) theme
        _last_theme = read_config('Theme', 'last_theme', literal_eval=False)
        if _last_theme:
            self.logger.info("Using 'last used' theme: {}".format(_last_theme))
            try:
                self.set_theme(_last_theme)
            except Exception as exc:
                self.logger.error("Failed setting 'last used' theme: {}".format(_last_theme), exc_info=exc)

        # Set the (last used) style
        _last_style = read_config('Theme', 'last_style', literal_eval=False)
        if _last_style:
            self.logger.info("Using 'last used' style: {}".format(_last_style))
            try:
                self.set_theme(_last_style, stylesheet=False)
            except Exception as exc:
                self.logger.error("Failed setting 'last used' style: {}".format(_last_style), exc_info=exc)

        # Add and populate menus
        self.menubar = self.add_menus()

        # Add and populate toolbar
        self.toolbar = self.add_toolbar()

        # Spawn the status bar instance
        self.statusBar()

        # Set MainWindow properties
        app_title = QMAINWINDOW_TITLE
        version = self.determine_version()
        if version:
            app_title += " v{}".format(version)
        self.setWindowTitle(app_title)
        self.setWindowIcon(QIcon(os.path.join(ICONS_PATH, QMAINWINDOW_ICON)))
        self.statusBar().showMessage('Ready.')

        # Add progress bar to the status bar
        progress_bar = self.main_model.create_progressbar_on_statusbar(self)
        progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(progress_bar)
        self.statusBar().addPermanentWidget(DbStateIcon(self.toolbar, self.main_model))

        # Add Views/CentralWidgets
        self.central_widget.addWidget(self.subfeed_grid_view)
        self.central_widget.addWidget(self.playback_grid_view)
        self.central_widget.addWidget(self.download_view)
        self.central_widget.addWidget(self.list_detailed_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.central_widget.addWidget(self.list_tiled_view)
        self.central_widget.addWidget(self.subscriptions_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.central_widget.addWidget(self.about_view)
        self.central_widget.addWidget(self.config_view)
        self.central_widget.setCurrentWidget(self.subfeed_grid_view)

    # Init UI Helpers
    def setup_views(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.subfeed_grid_view = GridScrollArea(self, self.main_model)
        self.playback_grid_view = GridScrollArea(self, self.main_model)
        self.subfeed_grid_view.set_view(SubfeedGridView(self.subfeed_grid_view, self, self.main_model), SUBFEED_VIEW_ID)
        self.playback_grid_view.set_view(PlaybackGridView(self.playback_grid_view, self, self.main_model),
                                         PLAYBACK_VIEW_ID)

        self.download_view = DownloadScrollArea(self, self.main_model)

        self.hotkeys_view = ConfigWindow(self)
        self.hotkeys_view.setWidget(HotkeysViewWidget(self.hotkeys_view, self,
                                                      icon=QIcon(os.path.join(ICONS_PATH, HOTKEYS_ICON))))
        self.config_view = ConfigViewTabs(self, icon=QIcon(os.path.join(ICONS_PATH, CONFIG_ICON)))

        self.list_detailed_view = SubfeedDetailedListView(self)
        self.list_tiled_view = SubfeedTiledListView(self)
        self.subscriptions_view = SubscriptionsDetailedListView(self)
        self.about_view = AboutView(self)

    # --- Menu
    def add_menus(self):
        """
        Adds menu items to the menu bar.
        :return: menubar
        """
        menubar = self.menuBar()
        self.add_menu_file(menubar)
        self.add_menu_function(menubar)
        self.add_menu_view(menubar)
        self.add_menu_window(menubar)
        self.add_menu_help(menubar)
        if read_config('Debug', 'debug'):
            self.add_menu_debug(menubar)

        return menubar

    def add_menu_file(self, menubar):
        """
        Adds the File menu to menu bar.
        :param menubar:
        :return:
        """
        self.add_menu(menubar, '&File')
        self.add_submenu('&File', 'Download by URL/ID', self.download_single_url_dialog,
                         shortcut=read_config('Global', 'download_video_by_url', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL), tooltip='Download a video by URL/ID')
        self.add_submenu('&File', 'Subscribe to a channel: ID', self.add_subscription_by_id_dialog,
                         tooltip='Local override: Subscribe to a channel by ID (Will *NOT* affect YouTube!)')
        self.add_submenu('&File', 'Subscribe to a channel: Username', self.add_subscription_by_username_dialog,
                         tooltip='Local override: Subscribe to a channel by Username (Will *NOT* affect YouTube!)')
        self.add_submenu('&File', 'View history', self.usage_history_dialog,
                         shortcut=read_config('Global', 'show_usage_history',
                                              custom_ini=HOTKEYS_INI, literal_eval=HOTKEYS_EVAL),
                         tooltip='Show usage history in a dialog box')
        self.add_submenu('&File', 'Exit', qApp.quit, shortcut=read_config('Global', 'quit', custom_ini=HOTKEYS_INI,
                                                                          literal_eval=HOTKEYS_EVAL),
                         tooltip='Exit application')

    def add_menu_function(self, menubar):
        """
        Adds the Function menu to menu bar.
        :param menubar:
        :return:
        """
        self.add_menu(menubar, '&Function')

        # Set function menu triggers
        self.add_submenu('&Function', 'Copy all URLs', self.clipboard_copy_urls,
                         shortcut=read_config('Global', 'copy_all_urls', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL),
                         tooltip='Copy URLs of all currently visible videos to clipboard', icon=COPY_ALL_URLS_ICON)

        # refresh_list
        self.toolbar_items['RefreshSubFeed'] = self.add_submenu('&Function', 'Refresh Feed',
                                                                self.emit_signal_with_set_args,
                                                                shortcut=read_config('Global', 'refresh_feed',
                                                                                     custom_ini=HOTKEYS_INI,
                                                                                     literal_eval=HOTKEYS_EVAL),
                                                                tooltip='Refresh the subscription feed',
                                                                icon=REFRESH_SUBFEED_ICON,
                                                                signal=self.main_model.main_window_listener.refreshVideos,
                                                                args=(LISTENER_SIGNAL_NORMAL_REFRESH,))

        self.add_submenu('&Function', 'Reload Subscriptions &List',
                         self.main_model.main_window_listener.refreshSubs.emit,
                         shortcut=read_config('Global', 'reload_subslist', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL),
                         tooltip='Fetch a new subscriptions list', icon=RELOAD_SUBS_LIST_ICON)

        # FIXME: icon, shortcut(alt/shift as extra modifier to the normal refresh shortcut?)
        self.add_submenu('&Function', 'Deep refresh of feed', self.emit_signal_with_set_args,
                         shortcut=read_config('Global', 'refresh_feed_deep', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL),
                         tooltip='Deed refresh the subscription feed', icon=REFRESH_SUBFEED_DEEP_ICON,
                         signal=self.main_model.main_window_listener.refreshVideos,
                         args=(LISTENER_SIGNAL_DEEP_REFRESH,))

        self.add_submenu('&Function', 'Test Channels', self.main_model.main_window_listener.testChannels.emit,
                         tooltip='Tests the test_pages and miss_limit of channels', icon=RERUN_TEST_ICON)

        if self.main_model.yt_dir_listener is not None:
            self.add_submenu('&Function', 'Manual dir search', self.main_model.yt_dir_listener.manualCheck.emit,
                             tooltip='Starts a manual search for new videos in youtube directory',
                             icon=MANUAL_DIR_SEARCH_ICON)

        thumb_tooltip = 'Starts a manual download of thumbnails for videos currently in play view and sub feed'
        self.add_submenu('&Function', 'Manual thumbnail download',
                         self.download_thumbnails_manually,
                         tooltip=thumb_tooltip, icon=MANUAL_THUMBS_DOWNLOAD_ICON)

        self.add_submenu('&Function', 'Manual DB grab', self.update_from_db,
                         tooltip='Starts a manual grab of data for the model', icon=DATABASE_ICON,
                         shortcut=read_config('Global', 'manual_db_grab', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL))

        # FIXME: icon, look more related to action
        self.add_submenu('&Function', 'Toggle sort-by: ascending date', self.toggle_sort_by_ascending,
                         tooltip='Toggles the ascending date config option, and does a manual re-grab',
                         icon=SORT_BY_ASC_DATE_ICON, shortcut=read_config('Playback', 'ascending_sort_toggle',
                                                                          custom_ini=HOTKEYS_INI,
                                                                          literal_eval=HOTKEYS_EVAL))
        self.add_submenu('&Function', 'Toggle sort-by: channel', self.toggle_sort_by_channel,
                         tooltip='Toggles the ascending date config option, and does a manual re-grab',
                         icon=SORT_BY_CHANNEL_ICON, shortcut=read_config('Playback', 'by_channel_sort_toggle',
                                                                         custom_ini=HOTKEYS_INI,
                                                                         literal_eval=HOTKEYS_EVAL))

        self.add_submenu('&Function', 'Log History 2.0', self.history_log,
                         tooltip='Send entire history to logger')
        self.add_submenu('&Function', 'Undo', self.history_undo,
                         tooltip='Undo previous action (if possible)',
                         icon=UNDO_ICON, shortcut=read_config('Global', 'history_undo_action',
                                                              custom_ini=HOTKEYS_INI, literal_eval=HOTKEYS_EVAL))

    def add_menu_view(self, menubar):
        """
        Adds the View menu to menu bar.
        :param menubar:
        :return:
        """
        self.add_menu(menubar, '&View')
        self.views['SubFeedGridView'] = self.add_submenu('&View', 'Subscription feed', self.set_current_widget,
                                                         shortcut=read_config('View', 'subfeed', custom_ini=HOTKEYS_INI,
                                                                              literal_eval=HOTKEYS_EVAL),
                                                         tooltip='View subscription feed as a grid',
                                                         icon=SUBFEED_VIEW_ICON, widget=self.subfeed_grid_view)
        self.views['PlaybackGridView'] = self.add_submenu('&View', 'Playback feed', self.set_current_widget,
                                                          shortcut=read_config('View', 'playback',
                                                                               custom_ini=HOTKEYS_INI,
                                                                               literal_eval=HOTKEYS_EVAL),
                                                          tooltip='View downloaded videos as a grid',
                                                          widget=self.playback_grid_view,
                                                          icon=PLAYBACK_VIEW_ICON)
        self.views['SubfeedDetailedListView'] = self.add_submenu('&View', 'Detailed List', self.set_current_widget,
                                                                 shortcut=read_config('View', 'detailed_list',
                                                                                      custom_ini=HOTKEYS_INI,
                                                                                      literal_eval=HOTKEYS_EVAL),
                                                                 tooltip='View subscription feed as a detailed list',
                                                                 icon=DETAILED_LIST_VIEW_ICON,
                                                                 widget=self.list_detailed_view)
        self.views['DownloadView'] = self.add_submenu('&View', 'Downloads', self.set_current_widget,
                                                      shortcut=read_config('View', 'download', custom_ini=HOTKEYS_INI,
                                                                           literal_eval=HOTKEYS_EVAL),
                                                      tooltip='Shows in progress downloads', icon=DOWNLOAD_VIEW_ICON,
                                                      widget=self.download_view)
        self.views['SubscriptionsDetailedListView'] = self.add_submenu('&View', 'Subscriptions',
                                                                       self.set_current_widget,
                                                                       shortcut=read_config('View', 'subscriptions',
                                                                                            custom_ini=HOTKEYS_INI,
                                                                                            literal_eval=HOTKEYS_EVAL),
                                                                       tooltip='View Subscriptions',
                                                                       icon=SUBS_LIST_VIEW_ICON,
                                                                       widget=self.subscriptions_view)
        self.views['ConfigView'] = self.add_submenu('&View', 'Configuration', self.set_current_widget,
                                                    shortcut=read_config('View', 'config',
                                                                         custom_ini=HOTKEYS_INI,
                                                                         literal_eval=HOTKEYS_EVAL),
                                                    tooltip='View or change program settings', icon=CONFIG_ICON,
                                                    widget=self.config_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.views['SubfeedTiledListView'] = self.add_submenu('&View', 'Tiled List', self.set_current_widget,
                                                                  shortcut=read_config('View', 'tiled_list',
                                                                                       custom_ini=HOTKEYS_INI,
                                                                                       literal_eval=HOTKEYS_EVAL),
                                                                  tooltip='View subscription feed as a tiled list',
                                                                  icon=SUBFEED_TILED_LIST_VIEW_ICON,
                                                                  widget=self.list_tiled_view)

    def add_menu_window(self, menubar):
        """
        Adds the Window menu to menu bar.
        :param menubar:
        :return:
        """
        # Window menu
        window_menu = self.add_menu(menubar, '&Window')
        # --- Theme submenu
        theme_submenu = self.add_menu(window_menu, 'Theme')
        self.add_submenu(theme_submenu, 'Cycle theme', self.cycle_themes, tooltip='Cycle theme', subsubmenu=True)
        self.add_submenu(theme_submenu, 'Default', self.set_theme_native, tooltip='Set theme to system default',
                         subsubmenu=True)
        self.add_submenu(theme_submenu, 'Breeze Light', self.set_theme_breeze_light,
                         tooltip='Set theme to Breeze Light',
                         subsubmenu=True)
        self.add_submenu(theme_submenu, 'Breeze Dark', self.set_theme_breeze_dark, tooltip='Set theme to Breeze Dark',
                         subsubmenu=True)
        # self.add_submenu_separator('&Theme')
        # --- Style submenu
        style_submenu = self.add_menu(window_menu, 'Style')
        self.add_available_qstyles_to_menu(style_submenu, subsubmenu=True)

    def add_menu_help(self, menubar):
        """
        Adds the Help menu to menu bar.
        :param menubar:
        :return:
        """
        self.add_menu(menubar, '&Help')
        self.add_submenu('&Help', 'Hotkeys', self.view_hotkeys,
                         shortcut=read_config('Global', 'hotkeys', custom_ini=HOTKEYS_INI, literal_eval=HOTKEYS_EVAL),
                         tooltip='View hotkeys', icon=HOTKEYS_ICON)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.views['About'] = self.add_submenu('&Help', 'About', self.set_current_widget, tooltip='About me',
                                                   icon=ABOUT_ICON, widget=self.about_view)

    def add_menu_debug(self, menubar):
        """
        Adds the Debug menu to menu bar.
        :param menubar:
        :return:
        """
        self.add_menu(menubar, '&Debug')
        self.add_submenu('&Debug', 'Raise a generic Exception (GUI)', self.debug_throw_exception,
                         tooltip='Oh dear..')
        self.add_submenu('&Debug', 'Raise (and don\'t catch) a generic Exception (GUI)',
                         self.debug_throw_and_dont_catch_exception, tooltip='Oh dear..')
        self.add_submenu('&Debug', 'Raise a generic Exception (Backend)', self.debug_throw_exception_backend,
                         tooltip='Oh dear..')
        self.add_submenu('&Debug', 'Poll Exceptions', self.poll_exceptions,
                         tooltip='Oh dear..')
        # self.add_submenu('&Debug', 'Open 1K FDs', debug_functions.open_1000_file_descriptors, tooltip="Uh oh..")

    # --- Toolbar
    def add_toolbar(self):
        """
        Adds toolbar items to the toolbar.

        Most of these are referencing menu items.
        :return: toolbar
        """
        toolbar = Toolbar(self)
        self.addToolBar(toolbar)
        toolbar.addAction(self.views['SubFeedGridView'])
        toolbar.addAction(self.views['PlaybackGridView'])
        toolbar.addAction(self.views['SubfeedDetailedListView'])
        toolbar.addAction(self.views['DownloadView'])
        toolbar.addAction(self.views['ConfigView'])
        if read_config('Debug', 'show_unimplemented_gui'):  # FIXME: Implement SubfeedTiledListView
            toolbar.addAction(self.views['SubfeedTiledListView'])
        toolbar.addAction(self.views['SubscriptionsDetailedListView'])
        if read_config('Debug', 'show_unimplemented_gui'):
            toolbar.addAction(self.views['About'])

        toolbar.create_action_group()
        # Items that should not be included in the exclusive action group.
        toolbar.addAction(self.toolbar_items['RefreshSubFeed'])

        return toolbar

    # Debug
    def debug_throw_exception(self):
        """
        Raises a generic Exception.
        :return:
        """
        try:
            raise Exception("Generic Exception (frontend)")
        except Exception as e:
            self.logger.info("Handled generic Exception in frontend", exc_info=e)

    def debug_throw_and_dont_catch_exception(self):
        """
        Raises a generic Exception.
        :return:
        """
        raise Exception("Generic Uncaught Exception (frontend)")

    def debug_throw_exception_backend(self):
        """
        Raises a generic Exception in the backend.
        :return:
        """
        try:
            self.sane_try(self.main_model.main_window_listener.raiseGenericException.emit)
        except Exception as e:
            self.logger.info("Handled generic backend Exception in frontend", exc_info=e)

    # Exception handling
    def raise_exception(self, exctype, value, this_traceback):
        """
        Raises an exception (usually called by the Exception Handler)
        :param exctype:
        :param value:
        :param this_traceback:
        :return:
        """
        if read_config('Debug', 'display_all_exceptions'):
            exc_info = copy.copy((exctype, value, this_traceback))
            self.exception_dialog(exc_info)
        else:
            raise exctype(exctype, value, this_traceback)

    def check_for_backend_exceptions(self):
        """
        Returns backend exceptions list (if any).
        :return:
        """
        return self.exceptionHandler.exceptions

    def sane_try(self, func, *args, **kwargs):
        """
        Reinventing the try/except wheel in order to raise exceptions in the right places.
        :param func: function to call
        :param args: args to pass
        :param kwargs: kwargs to pass
        :return:
        """
        if args and kwargs:
            func(args, kwargs)
        elif args and not kwargs:
            if len(args) == 1:
                func(args[0])
            else:
                func(args)
        elif kwargs and not args:
            func(kwargs)
        else:
            func()
        backend_exceptions = self.check_for_backend_exceptions()
        if len(backend_exceptions) != 0:
            exc_type, value, this_traceback = self.exceptionHandler.pop_exception()
            raise exc_type(exc_type, value, this_traceback)

    def poll_exceptions(self, auto_clear=False):
        """
        Polls the exceptions list from Exception Handler
        :param auto_clear: Clears the list unless False
        :return:
        """
        # Make a proper copy instead of just referencing the list (that may get auto cleared)
        retv = copy.copy(self.exceptionHandler.exceptions)
        self.logger.info("Polled exceptions")
        self.logger.info(retv)
        if auto_clear:
            self.main_model.clear_exceptions()
            self.logger.debug("(Auto) Cleared exception list")
        return retv

    @staticmethod
    def rebuild_traceback(exc_info):
        """
        Reshuffles the traceback bits into a more sensible order, making it look like the actual thing.
        :param exc_info: Exception tuple
        :return:
        """
        exctype, value, this_traceback = exc_info
        tb_str = traceback.format_stack()
        exc_str = traceback.format_exception(exctype, value, this_traceback)

        # Pop the Traceback info header from exception and put it at the top of string list
        tb_str[0:0] = exc_str.pop(0)
        tb_str.extend(exc_str)

        return ''.join(tb_str)

    def exception_dialog(self, exc_info):
        """
        Pop-up a SaneTextViewDialog with Exception information.
        :return:
        """
        exctype, value, this_traceback = exc_info
        window_title = "An unexpected {} has occurred!".format(exctype)

        exception_dialog = SaneTextViewDialog(self, self.rebuild_traceback(exc_info))
        exception_dialog.setWindowTitle(window_title)
        exception_dialog.show()

    # Version Control
    def determine_version(self):
        """
        Attempt to determine current release version based on VERSION.txt (and git).
        :return:
        """
        git_branchtag = self.get_git_tag()
        try:
            with open(VERSION_PATH, 'r') as version_file:
                version = version_file.readline()
                if git_branchtag:
                    version_str = "{} [{}]".format(str(version), git_branchtag)
                else:
                    version_str = str(version)
        except Exception as e:
            self.logger.critical("An unhandled exception occurred!", exc_info=e)
            self.exception_dialog(copy.copy(sys.exc_info()))
            return "N/A"

        return version_str

    def get_git_tag(self):
        """
        Retrieves git branch/commit_tag if in a git environment.
        :return:
        """
        try:
            branch_tag = check_output("git rev-parse --abbrev-ref HEAD", shell=True).decode("UTF-8").strip('\n') + ' / '
        except Exception as e:
            self.logger.critical("An unhandled exception occurred!", exc_info=e)
            return "N/A"
        try:
            branch_tag += check_output("git log -n 1 --pretty=format:%h", shell=True).decode("UTF-8").strip('\n')
        except Exception as e2:
            self.logger.critical("An unhandled exception occurred!", exc_info=e2)
            self.exception_dialog(copy.copy(sys.exc_info()))
            return "N/A"

        return branch_tag

    # Theme handling
    def set_theme(self, theme, stylesheet=True):
        """
        Applies a QStyle or QStyleSheet to the QApplication
        :param stylesheet:
        :param theme:
        :return:
        """
        if stylesheet:
            theme_file = QFile(theme)
            theme_file.open(QFile.ReadOnly | QFile.Text)
            theme_stream = QTextStream(theme_file)
            self.app.setStyleSheet(theme_stream.readAll())
            set_config('Theme', 'last_theme', theme)
        else:
            self.app.setStyle(QStyleFactory.create(theme))
            set_config('Theme', 'last_style', theme)
        self.current_theme = theme

    def set_theme_native(self):
        """
        Reset the theme to default/native.
        :return:
        """
        self.set_theme(None)

    def set_theme_breeze_dark(self):
        self.set_theme(themes.BREEZE_DARK)

    def set_theme_breeze_light(self):
        self.set_theme(themes.BREEZE_LIGHT)

    def add_available_qstyles_to_menu(self, menu, subsubmenu=False):
        """
        Populates the given menu with all available QStyles.
        :param menu:
        :param subsubmenu:
        :return:
        """
        for name, _ in QSTYLES_AVAILABLE.items():
            action = self.set_qstyle

            self.logger.info("Adding available QStyle '{}' to '{}' menu.".format(name, menu))
            self.add_submenu(menu, name, action, tooltip="Apply the '{}' theme.".format(name), subsubmenu=subsubmenu,
                             qstyle=name)

    def set_qstyle(self, q_style):
        """
        Sets theme to a QStyle.
        :param q_style:
        :return:
        """
        self.set_theme(q_style, stylesheet=False)

    def cycle_themes(self):
        """
        Cycles through the available themes.
        :return:
        """
        if self.current_theme_idx >= len(self.themes_list) - 1:
            self.current_theme_idx = -1

        self.current_theme_idx += 1
        self.set_theme(self.themes_list[self.current_theme_idx])
        self.logger.info("Cycled to theme: '{}'".format(self.themes_list[self.current_theme_idx]))

    # Menu handling
    def add_menu(self, menubar, name, submenu=False):
        """
        Adds a menu and an optional amount of submenus
        :param submenu: If True menu is child of another menu.
        :param menubar:
        :param name:
        :return:
        """
        if submenu:
            this_submenu = menubar.addMenu(name)
            return this_submenu
        else:
            self.menus[name] = menubar.addMenu(name)
            return self.menus[name]

    def add_submenu(self, menu: str, name: str, action, shortcut=None, shortcuts=None,
                    tooltip=None, icon=None, subsubmenu=False, dummy=False, disabled=False, **kwargs):
        """
        Adds a submenu to a menu with optional properties.
        :param disabled:    Menu is disabled/greyed out.
        :param dummy:       Menu has no action bind.
        :param shortcuts:   Keyboard hotkey.
        :param subsubmenu:  If True submenu is child of a parent submenu.
        :param name:        Name to give this submenu.
        :param icon:        Icon filename (with relative path)
        :param tooltip:     String to show on statusbar/on-hover.
        :param action:      Function to bind action to.
        :param shortcut:    String on the form of '<key>+...n+key>' e.g. 'Ctrl+1'
        :param menu:        String identifier (name) of the Menu to attach this submenu to.
        :return:
        """
        if icon:
            this_icon = QIcon(os.path.join(ICONS_PATH, icon))
        else:
            this_icon = None

        submenu = SaneToolBarAction(self, name, action, icon=this_icon, **kwargs)
        if shortcut:
            submenu.setShortcut(shortcut)
        elif shortcuts:
            submenu.setShortcuts(shortcuts)
        if tooltip:
            submenu.setStatusTip(tooltip)
        if subsubmenu:
            menu.addAction(submenu)
        else:
            if menu in self.menus:
                self.menus[menu].addAction(submenu)
            else:
                raise ValueError("add_submenu('{}', '{}', ...) ERROR: '{}' not in menus dict!".format(menu, name, menu))
        return submenu  # Used by toolbar, to avoid redefining items.

    def add_submenu_separator(self, menu):
        """
        Adds a separator item in a submenu.
        :param menu:
        :return:
        """
        self.menus[menu].addSeparator()

    def set_current_widget(self, widget):
        """
        Sets self.central_widget to reference the widget you want to show.
        :param widget:
        :return:
        """
        self.central_widget.setCurrentWidget(widget)

    def view_hotkeys(self):
        """
        Set View variable and CentralWidget to HotkeysView
        :return:
        """
        self.hotkeys_view.show()

    # Function menu functions
    def clipboard_copy_urls(self):
        """
        Adds the url of each video in the view to a string, separated by newline and puts it on clipboard.
        :return:
        """
        urls = ""
        for q_label in self.subfeed_grid_view.q_labels:
            urls += "{}\n".format(q_label.video.url_video)

        self.logger.info("Copied URLs to clipboard: \n{}".format(urls))
        self.clipboard.setText(urls)
        self.statusBar().showMessage('Copied {} URLs to clipboard'.format(len(urls.splitlines())))

    def emit_signal_with_set_args(self, signal, args):
        """
        Takes a signal and emits it with the set args as *args
        :param signal:
        :param args:
        :return:
        """
        signal.emit(*args)

    def toggle_sort_by_ascending(self):
        """
        Sends a testChannels signal
        :return:
        """
        toggle = read_config('PlaySort', 'ascending_date')
        set_config('PlaySort', 'ascending_date', format(not toggle))
        self.main_model.playback_grid_view_listener.updateFromDb.emit()

    def toggle_sort_by_channel(self):
        """
        Sends a testChannels signal
        :return:
        """
        toggle = read_config('PlaySort', 'by_channel')
        set_config('PlaySort', 'by_channel', format(not toggle))
        self.main_model.playback_grid_view_listener.updateFromDb.emit()

    def history_log(self):
        """
        Sends entire SaneHistory to logger
        :return:
        """
        self.history.log()

    def history_undo(self, index=None):
        """
        Undoes the last action logged by SaneHistory (if possible)
        :param index:
        :return:
        """
        if index:
            self.history.undo(index)
        else:
            self.history.undo()

    def download_thumbnails_manually(self):
        """
        Starts a manual download of thumbnails for videos currently in play view and sub feed.
        :return:
        """
        self.main_model.subfeed_grid_view_listener.thumbnailDownload.emit()
        self.main_model.playback_grid_view_listener.thumbnailDownload.emit()

    def update_from_db(self):
        """
        Starts a manual grab of data for the model.
        :return:
        """
        self.main_model.subfeed_grid_view_listener.updateFromDb.emit()
        self.main_model.playback_grid_view_listener.updateFromDb.emit()

    # File menu functions

    def add_subscription_by_id(self, input_text):
        """
        Add a YouTube subscription (On YouTube).
        :param input_text: URL or ID
        :return:
        """
        self.main_model.main_window_listener.addYouTubeChannelSubscriptionById.emit(input_text)

    def add_subscription_by_username(self, input_text):
        """
        Add a YouTube subscription (On YouTube).
        :param input_text: URL or ID
        :return:
        """
        self.main_model.main_window_listener.addYouTubeChannelSubscriptionByUsername.emit(input_text)

    def confirmation_dialog(self, message, actions, caller=None, title=None, ok_text='Yes', cancel_text='No'):
        """
        Prompts user for a Yes/No Confirmation where Yes results in a call for each action in actions
        :param message: Text to display in dialog body.
        :param actions: A function, or a list of functions to be called
        :param caller: (If given) applies action to the caller function e.g. action(caller)
        :param title: Title of dialog window.
        :param ok_text: Text to display on OK button.
        :param cancel_text: Text to display on Cancel button.
        :return:
        """
        if not title:
            title = "Are you sure?"
        dialog = SaneConfirmationDialog(self, actions, caller=caller, title=title, text=message,
                                        ok_text=ok_text, cancel_text=cancel_text)
        dialog.show()

    def download_single_url_dialog(self):
        """
        Prompts user for downloading a video by URL/ID
        :return:
        """
        input_dialog = SaneInputDialog(self, self.main_model.main_window_listener.getSingleVideo.emit,
                                       title='Download a video by URL/ID',
                                       text='Enter a YouTube URL or ID', ok_text='Download',
                                       validator=QRegExpValidator(YOUTUBE_URL_REGEX))
        input_dialog.show()

    def add_subscription_by_id_dialog(self):
        """
        Prompts user for a channel ID to add a YouTube subscription to.
        :return:
        """
        input_dialog = SaneInputDialog(self, self.add_subscription_by_id,
                                       title='[Local] Subscribe to channel: ID',
                                       text='[Local] Subscribe to channel by ID:', ok_text='Subscribe')
        input_dialog.show()

    def add_subscription_by_username_dialog(self):
        """
        Prompts user for a username to add a YouTube subscription to.
        :return:
        """
        input_dialog = SaneInputDialog(self, self.add_subscription_by_username,
                                       title='[Local] Subscribe to channel: Username',
                                       text='[Local] Subscribe to channel by username:', ok_text='Subscribe')
        input_dialog.show()

    def usage_history_dialog(self):
        """
        Pop-up a SaneTextViewDialog with usage history
        :return:
        """
        history = get_plaintext_history()
        history_dialog = SaneTextViewDialog(self, history)
        history_dialog.setWindowTitle("Usage history")
        history_dialog.show()
