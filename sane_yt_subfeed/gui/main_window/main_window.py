# !/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from subprocess import check_output

from PyQt5.QtCore import QFile, QTextStream, QRegExp
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QMenu, QStackedWidget, QStyleFactory

# Project internal libs
from sane_yt_subfeed.absolute_paths import ICONS_PATH, VERSION_PATH
from sane_yt_subfeed.config_handler import read_config, set_config
from sane_yt_subfeed.controller.listeners.listeners import LISTENER_SIGNAL_NORMAL_REFRESH, LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.controller.static_controller_vars import GRID_VIEW_ID, PLAY_VIEW_ID
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.dialogs.sane_input_dialog import SaneInputDialog
from sane_yt_subfeed.gui.dialogs.text_view_dialog import TextViewDialog
from sane_yt_subfeed.gui.main_window.db_state import DbStateIcon
from sane_yt_subfeed.gui.main_window.toolbar import Toolbar
from sane_yt_subfeed.gui.main_window.toolbar_action import SaneToolBarAction
from sane_yt_subfeed.gui.themes import themes
from sane_yt_subfeed.gui.themes.themes import THEMES_LIST, QSTYLES_AVAILABLE
from sane_yt_subfeed.gui.views.about_view import AboutView
from sane_yt_subfeed.gui.views.config_view.config_view_tabs import ConfigViewTabs
from sane_yt_subfeed.gui.views.config_view.config_window import ConfigWindow
from sane_yt_subfeed.gui.views.config_view.views.hotkeys_view import HotkeysViewWidget
from sane_yt_subfeed.gui.views.download_view.dl_scroll_area import DownloadScrollArea
from sane_yt_subfeed.gui.views.grid_view.grid_scroll_area import GridScrollArea
from sane_yt_subfeed.gui.views.grid_view.play_view.play_view import PlayView
from sane_yt_subfeed.gui.views.grid_view.sub_feed.sub_feed_view import SubFeedView
from sane_yt_subfeed.gui.views.list_detailed_view import ListDetailedView
from sane_yt_subfeed.gui.views.list_tiled_view import ListTiledView
from sane_yt_subfeed.gui.views.subscriptions_view import SubscriptionsView
from sane_yt_subfeed.history_handler import get_history
from sane_yt_subfeed.log_handler import create_logger

# Constants
HOTKEYS_EVAL = False
HOTKEYS_INI = 'hotkeys'
YOUTUBE_URL_REGEX = QRegExp('(http[s]?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/[^ ]+')
YOUTUBE_URL_REGEX.setCaseSensitivity(False)


class MainWindow(QMainWindow):
    current_view = None
    grid_view = None
    subs_view = None
    list_detailed_view = None
    list_tiled_view = None
    about_view = None
    menus = None
    hotkey_ctrl_down = False

    # noinspection PyArgumentList
    def __init__(self, app: QApplication, main_model: MainModel, dimensions=None, position=None):
        super().__init__()
        self.logger = create_logger(__name__)
        self.app = app
        self.main_model = main_model

        self.themes_list = THEMES_LIST
        self.current_theme = None
        self.current_theme_idx = 0
        self.bgcolor = read_config('Gui', 'bgcolor', literal_eval=False)

        self.clipboard = QApplication.clipboard()
        self.status_bar = self.statusBar()
        self.menus = {}
        if dimensions:
            self.dimensions = dimensions
        else:
            self.dimensions = [770, 700]
        self.position = position
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.grid_view = GridScrollArea(self, main_model)
        self.play_view = GridScrollArea(self, main_model)
        self.grid_view.set_view(SubFeedView(self.grid_view, self, main_model), GRID_VIEW_ID)
        self.play_view.set_view(PlayView(self.play_view, self, main_model), PLAY_VIEW_ID)

        self.download_view = DownloadScrollArea(self, main_model)

        self.hotkeys_view = ConfigWindow(self)
        self.hotkeys_view.setWidget(HotkeysViewWidget(self.hotkeys_view, self,
                                                      icon=QIcon(os.path.join(ICONS_PATH, 'hotkeys.png'))))
        self.config_view = ConfigViewTabs(self, icon=QIcon(os.path.join(ICONS_PATH, 'preferences.png')))

        self.list_detailed_view = ListDetailedView(self)
        self.list_tiled_view = ListTiledView(self)
        self.subs_view = SubscriptionsView(self)
        self.about_view = AboutView(self)

        self.init_ui()

    def init_ui(self):
        self.logger.info("Initialized UI")

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

        # Define a menu and status bar
        menubar = self.menuBar()
        self.statusBar()

        # File menu
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
        self.add_submenu('&File', 'Preferences', self.view_config,
                         shortcut=read_config('Global', 'preferences', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL),
                         tooltip='Change application settings', icon='preferences.png')
        self.add_submenu('&File', 'Exit', qApp.quit, shortcut=read_config('Global', 'quit', custom_ini=HOTKEYS_INI,
                                                                          literal_eval=HOTKEYS_EVAL),
                         tooltip='Exit application')

        # Function menu
        self.add_menu(menubar, '&Function')

        # Set function menu triggers
        self.add_submenu('&Function', 'Copy all URLs', self.clipboard_copy_urls,
                         shortcut=read_config('Global', 'copy_all_urls', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL),
                         tooltip='Copy URLs of all currently visible videos to clipboard', icon='copy.png')

        # refresh_list
        refresh_feed = self.add_submenu('&Function', 'Refresh Feed', self.emit_signal_with_set_args,
                                        shortcut=read_config('Global', 'refresh_feed', custom_ini=HOTKEYS_INI,
                                                             literal_eval=HOTKEYS_EVAL),
                                        tooltip='Refresh the subscription feed', icon='refresh.png',
                                        signal=self.main_model.main_window_listener.refreshVideos,
                                        args=(LISTENER_SIGNAL_NORMAL_REFRESH,))

        self.add_submenu('&Function', 'Reload Subscriptions &List',
                         self.main_model.main_window_listener.refreshSubs.emit,
                         shortcut=read_config('Global', 'reload_subslist', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL),
                         tooltip='Fetch a new subscriptions list', icon='refresh_subs.png')

        # FIXME: icon, shortcut(alt/shift as extra modifier to the normal refresh shortcut?)
        self.add_submenu('&Function', 'Deep refresh of feed', self.emit_signal_with_set_args,
                         shortcut=read_config('Global', 'refresh_feed_deep', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL),
                         tooltip='Deed refresh the subscription feed', icon='refresh.png',
                         signal=self.main_model.main_window_listener.refreshVideos,
                         args=(LISTENER_SIGNAL_DEEP_REFRESH,))

        self.add_submenu('&Function', 'Test Channels', self.main_model.main_window_listener.testChannels.emit,
                         tooltip='Tests the test_pages and miss_limit of channels', icon='rerun_test.png')

        self.add_submenu('&Function', 'Manual dir search', self.main_model.yt_dir_listener.manualCheck.emit,
                         tooltip='Starts a manual search for new videos in youtube directory',
                         icon='folder_refresh.png')

        thumb_tooltip = 'Starts a manual download of thumbnails for videos currently in play view and sub feed'
        self.add_submenu('&Function', 'Manual thumbnail download',
                         self.main_model.grid_view_listener.thumbnailDownload.emit,
                         tooltip=thumb_tooltip, icon='folder_refresh.png')

        self.add_submenu('&Function', 'Manual DB grab', self.main_model.grid_view_listener.updateFromDb.emit,
                         tooltip='Starts a manual grab of data for the model', icon='database.png',
                         shortcut=read_config('Global', 'manual_db_grab', custom_ini=HOTKEYS_INI,
                                              literal_eval=HOTKEYS_EVAL))

        # FIXME: icon, look more related to action
        self.add_submenu('&Function', 'Toggle ascending date', self.toggle_ascending_sort,
                         tooltip='Toggles the ascending date config option, and does a manual re-grab',
                         icon='database.png', shortcut=read_config('Playback', 'ascending_sort_toggle',
                                                                   custom_ini=HOTKEYS_INI, literal_eval=HOTKEYS_EVAL))

        # get_single_video = self.add_submenu('&Function', 'Get video', self.get_single_video,
        #                                     tooltip='Fetch video by URL')

        # View menu
        self.add_menu(menubar, '&View')
        view_grid_view = self.add_submenu('&View', 'Subscription feed', self.set_current_widget,
                                          shortcut=read_config('View', 'subfeed', custom_ini=HOTKEYS_INI,
                                                               literal_eval=HOTKEYS_EVAL),
                                          tooltip='View subscription feed as a grid', icon='grid.png',
                                          widget=self.grid_view)
        view_play_view = self.add_submenu('&View', 'Playback feed', self.set_current_widget,
                                          shortcut=read_config('View', 'playback', custom_ini=HOTKEYS_INI,
                                                               literal_eval=HOTKEYS_EVAL),
                                          tooltip='View downloaded videos as a grid', widget=self.play_view,
                                          icon='play_view_basic.png')
        view_list_detailed_view = self.add_submenu('&View', 'Detailed List', self.set_current_widget,
                                                   shortcut=read_config('View', 'detailed_list', custom_ini=HOTKEYS_INI,
                                                                        literal_eval=HOTKEYS_EVAL),
                                                   tooltip='View subscription feed as a detailed list',
                                                   icon='table.png', widget=self.list_detailed_view)
        view_downloads_view = self.add_submenu('&View', 'Downloads', self.set_current_widget,
                                               shortcut=read_config('View', 'download', custom_ini=HOTKEYS_INI,
                                                                    literal_eval=HOTKEYS_EVAL),
                                               tooltip='Shows in progress downloads', icon='download_view.png',
                                               widget=self.download_view)
        view_subs_view = self.add_submenu('&View', 'Subscriptions', self.set_current_widget,
                                          shortcut=read_config('View', 'subscriptions', custom_ini=HOTKEYS_INI,
                                                               literal_eval=HOTKEYS_EVAL),
                                          tooltip='View Subscriptions', icon='subs.png', widget=self.subs_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            view_list_tiled_view = self.add_submenu('&View', 'Tiled List', self.set_current_widget,
                                                    shortcut=read_config('View', 'tiled_list', custom_ini=HOTKEYS_INI,
                                                                         literal_eval=HOTKEYS_EVAL),
                                                    tooltip='View subscription feed as a tiled list',
                                                    icon='tiled_list.png', widget=self.list_tiled_view)

        # Window menu
        window_menu = self.add_menu(menubar, '&Window')
        #   Theme submenu
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
        #   Style submenu
        style_submenu = self.add_menu(window_menu, 'Style')
        self.add_available_qstyles_to_menu(style_submenu, subsubmenu=True)

        # Help menu
        self.add_menu(menubar, '&Help')
        self.add_submenu('&Help', 'Hotkeys', self.view_hotkeys,
                         shortcut=read_config('Global', 'hotkeys', custom_ini=HOTKEYS_INI, literal_eval=HOTKEYS_EVAL),
                         tooltip='View hotkeys', icon='hotkeys.png')
        if read_config('Debug', 'show_unimplemented_gui'):
            view_about_view = self.add_submenu('&Help', 'About', self.set_current_widget, tooltip='About me',
                                               icon='about.png', widget=self.about_view)

        toolbar = Toolbar(self)
        self.addToolBar(toolbar)
        toolbar.addAction(view_grid_view)
        toolbar.addAction(view_play_view)
        toolbar.addAction(view_list_detailed_view)
        toolbar.addAction(view_downloads_view)
        if read_config('Debug', 'show_unimplemented_gui'):  # FIXME: Implement
            toolbar.addAction(view_list_tiled_view)
        toolbar.addAction(view_subs_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            toolbar.addAction(view_about_view)

        toolbar.create_action_group()
        # not included in exclusive action group
        toolbar.addAction(refresh_feed)

        # Set MainWindow properties
        app_title = 'Sane Subscription Feed'
        version = self.determine_version()
        if version:
            app_title += " v{}".format(version)
        self.setWindowTitle(app_title)
        self.setWindowIcon(QIcon(os.path.join(ICONS_PATH, 'yubbtubbz-padding.ico')))
        self.statusBar().showMessage('Ready.')

        progress_bar = self.main_model.new_status_bar_progress(self)
        # progress_bar.setFixedHeight(20)
        progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(progress_bar)
        self.statusBar().addPermanentWidget(DbStateIcon(toolbar, self.main_model))

        # # Set a default view and layout
        # window_layout = QVBoxLayout()
        # self.view_grid()
        # self.setLayout(window_layout)

        # Display the window
        self.central_widget.addWidget(self.grid_view)
        self.central_widget.addWidget(self.play_view)
        self.central_widget.addWidget(self.download_view)
        self.central_widget.addWidget(self.list_detailed_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.central_widget.addWidget(self.list_tiled_view)
        self.central_widget.addWidget(self.subs_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.central_widget.addWidget(self.about_view)
        # self.central_widget.addWidget(self.hotkeys_view)
        self.central_widget.setCurrentWidget(self.grid_view)

        # if self.dimensions:
        #     self.resize(self.dimensions[0], self.dimensions[1])

    # Internal
    def determine_version(self):
        """
        Attempt to determine current release version based on VERSION.txt (and git)
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
            return "N/A"

        return version_str

    def get_git_tag(self):
        """
        Gets git branch/commit_tag if in a git environment
        :return:
        """
        try:
            branchtag = check_output("git rev-parse --abbrev-ref HEAD", shell=True).decode("UTF-8").strip('\n') + ' / '
        except Exception as e:
            self.logger.critical("An unhandled exception occurred!", exc_info=e)
            return "N/A"
        try:
            branchtag += check_output("git log -n 1 --pretty=format:%h", shell=True).decode("UTF-8").strip('\n')
        except Exception as e2:
            self.logger.critical("An unhandled exception occurred!", exc_info=e2)
            return "N/A"

        return branchtag

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
        self.set_theme(None)

    def set_theme_breeze_dark(self):
        self.set_theme(themes.BREEZE_DARK)

    def set_theme_breeze_light(self):
        self.set_theme(themes.BREEZE_LIGHT)

    def add_available_qstyles_to_menu(self, menu, subsubmenu=False):
        for name, _ in QSTYLES_AVAILABLE.items():
            action = self.set_qstyle

            self.logger.info("Adding available QStyle '{}' to '{}' menu.".format(name, menu))
            self.add_submenu(menu, name, action, tooltip="Apply the '{}' theme.".format(name), subsubmenu=subsubmenu,
                             qstyle=name)

    def set_qstyle(self, qstyle):
        self.set_theme(qstyle, stylesheet=False)

    def cycle_themes(self):
        if self.current_theme_idx >= len(self.themes_list) - 1:
            self.current_theme_idx = -1

        self.current_theme_idx += 1
        self.set_theme(self.themes_list[self.current_theme_idx])
        self.logger.info("Cycled to theme: '{}'".format(self.themes_list[self.current_theme_idx]))

    # Menu handling
    def add_menu(self, menubar, name, submenu=False):
        """
        Adds a menu and an optional amount of submenus
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

    def add_submenu(self, menu, name, action, shortcut=None, shortcuts=None,
                    tooltip=None, icon=None, subsubmenu=False, dummy=False, **kwargs):
        """
        Adds a submenu with optional properties to a menu
        :param subsubmenu:
        :param name:
        :param icon: icon filename (with relative path)
        :param tooltip: String
        :param action: Function
        :param shortcut: String on the form of '<key>+...n+key>' e.g. 'Ctrl+1'
        :param menu:
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
        return submenu  # FIXME: Used by toolbar to avoid redefining items

    def add_submenu_separator(self, menu):
        self.menus[menu].addSeparator()

    @staticmethod
    def hide_widget(widget):  # TODO: Deferred usage (Garbage collection issue)
        """
        Hides a widget/view
        :param widget:
        :return:
        """
        widget.setHidden(True)

    def set_current_widget(self, widget):
        self.central_widget.setCurrentWidget(widget)

    def view_config(self):
        """
        Set View variable and CentralWidget to ConfigView
        :return:
        """
        self.config_view.show()
        # self.central_widget.setCurrentWidget(self.config_view)

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
        for q_label in self.grid_view.q_labels:
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

    def toggle_ascending_sort(self):
        """
        Sends a testChannels signal
        :return:
        """
        toggle = read_config('PlaySort', 'ascending_date')
        set_config('PlaySort', 'ascending_date', format(not toggle))
        self.main_model.grid_view_listener.updateFromDb.emit()

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
        Pop-up a TextViewDialog with usage history
        :return:
        """
        history = get_history()
        history_dialog = TextViewDialog(self, history)
        history_dialog.setWindowTitle("Usage history")
        history_dialog.show()

    # Unused functions
    def context_menu_event(self, event):  # TODO: Unused, planned usage in future
        """
        Context menu for right clicking video thumbnails and more.
        :param event:
        :return:
        """
        cmenu = QMenu(self)
        copy_link_action = cmenu.addAction("Copy link")
        open_link_action = cmenu.addAction("Open link")
        close_action = cmenu.addAction("Close")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

    # Misc cleanup handling
    @staticmethod
    def clear_layout(layout):  # TODO: Unused
        """
        Deletes the given layout
        :param layout:
        :return:
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
