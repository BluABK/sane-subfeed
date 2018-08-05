# !/usr/bin/python3
# -*- coding: utf-8 -*-

# std libs
import os

# PyQt5 libs
from subprocess import check_output

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QMenu, QVBoxLayout, QStackedWidget, QProgressBar
from PyQt5.QtGui import QIcon

# Project internal libs
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners import LISTENER_SIGNAL_NORMAL_REFRESH, LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.database.read_operations import refresh_and_get_newest_videos
from sane_yt_subfeed.gui.views.about_view import AboutView
from sane_yt_subfeed.gui.views.config_view.config_view import ConfigView
from sane_yt_subfeed.gui.views.play_view.play_view import PlayView
from sane_yt_subfeed.gui.views.subscriptions_view import SubscriptionsView
from sane_yt_subfeed.youtube.thumbnail_handler import thumbnails_dl_and_paths
# from sane_yt_subfeed.uploads import Uploads
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView
from sane_yt_subfeed.gui.views.list_detailed_view import ListDetailedView
from sane_yt_subfeed.gui.views.list_tiled_view import ListTiledView
from sane_yt_subfeed.log_handler import create_logger

# Constants
OS_PATH = os.path.dirname(__file__)
ICO_PATH = os.path.join(OS_PATH, 'icons')


class MainWindow(QMainWindow):
    subs = []
    current_view = None
    grid_view = None
    subs_view = None
    list_detailed_view = None
    list_tiled_view = None
    about_view = None
    menus = None
    hotkey_ctrl_down = False

    # noinspection PyArgumentList
    def __init__(self, main_model: MainModel, dimensions=None, position=None):
        super().__init__()
        self.logger = create_logger("MainWindow")
        self.main_model = main_model

        for fakech in range(100):
            self.subs.append("Fake channel #{:3d}".format(fakech))
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

        self.grid_view = GridView(self, main_model)
        self.play_view = PlayView(self, main_model)
        self.list_detailed_view = ListDetailedView(self)
        self.list_tiled_view = ListTiledView(self)
        self.subs_view = SubscriptionsView(self)
        self.config_view = ConfigView(self)
        self.about_view = AboutView(self)

        self.init_ui()

    def init_ui(self):
        self.logger.info("Initialized UI")
        # Define a menu and status bar
        menubar = self.menuBar()
        self.statusBar()

        # File menu
        self.add_menu(menubar, '&File')
        self.add_submenu('&File', 'Exit', qApp.quit, shortcut='Ctrl+Q', tooltip='Exit application')

        view_config_view = self.add_submenu('&File', 'Preferences', self.view_config, shortcut='Ctrl+P',
                                            tooltip='Change application settings')
        # Function menu
        self.add_menu(menubar, '&Function')

        # Set function menu triggers
        self.add_submenu('&Function', 'Copy all URLs', self.clipboard_copy_urls, shortcut='Ctrl+D',
                         tooltip='Copy URLs of all currently visible videos to clipboard', icon='copy.png')

        # refresh_list
        # self.add_submenu('&Function', 'Refresh Feed', self.refresh_list, shortcut='Ctrl+R',
        #                  tooltip='Refresh the subscription feed'
        refresh_feed = self.add_submenu('&Function', 'Refresh Feed', self.refresh_list, shortcut='Ctrl+R',
                                        tooltip='Refresh the subscription feed', icon='refresh.png')

        self.add_submenu('&Function', 'Reload Subscriptions &List', self.refresh_subs, shortcut='Ctrl+L',
                         tooltip='Fetch a new subscriptions list', icon='refresh_subs.png')

        # FIXME: icon, shortcut(alt/shift as extra modifier to the normal refresh shortcut?)
        self.add_submenu('&Function', 'Deep refresh of feed', self.refresh_list_deep, shortcut='Ctrl+T',
                         tooltip='Deed refresh the subscription feed', icon='refresh.png')

        self.add_submenu('&Function', 'Test Channels', self.test_channels,
                         tooltip='Tests the test_pages and miss_limit of channels', icon='rerun_test.png')

        self.add_submenu('&Function', 'Manual dir search', self.dir_search,
                         tooltip='Starts a manual search for new videos in youtube directory',
                         icon='folder_refresh.png')

        # FIXME: icon, look more related to action
        self.add_submenu('&Function', 'Manual DB grab', self.db_reload,
                         tooltip='Starts a manual grab of data for the model', icon='database.png')
        # View menu
        self.add_menu(menubar, '&View')
        view_grid_view = self.add_submenu('&View', 'Subscription feed', self.view_grid, shortcut='Ctrl+1',
                                          tooltip='View subscription feed as a grid', icon='grid.png')
        view_play_view = self.add_submenu('&View', 'Playable videos feed', self.view_play, shortcut='Ctrl+2',
                                          tooltip='View downloaded videos as a grid',
                                          icon='play_view_basic.png')
        view_list_detailed_view = self.add_submenu('&View', 'Detailed List', self.view_list_detailed, shortcut='Ctrl+3',
                                                   tooltip='View subscription feed as a detailed list',
                                                   icon='table.png')
        if read_config('Debug', 'show_unimplemented_gui'):
            view_list_tiled_view = self.add_submenu('&View', 'Tiled List', self.view_list_tiled, shortcut='Ctrl+4',
                                                    tooltip='View subscription feed as a tiled list',
                                                    icon='tiled_list.png')
        view_subs_view = self.add_submenu('&View', 'Subscriptions', self.view_subs, shortcut='Ctrl+5',
                                          tooltip='View Subscriptions', icon='subs.png')

        # Help menu
        if read_config('Debug', 'show_unimplemented_gui'):
            self.add_menu(menubar, '&Help')
            view_about_view = self.add_submenu('&Help', 'About', self.view_about, shortcut='F1', tooltip='About me',
                                               icon='about.png')

        # Toolbar of different views
        toolbar = self.addToolBar('View')
        toolbar.addAction(view_grid_view)
        toolbar.addAction(view_play_view)
        toolbar.addAction(view_list_detailed_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            toolbar.addAction(view_list_tiled_view)
        toolbar.addAction(view_subs_view)
        toolbar.addAction(refresh_feed)
        if read_config('Debug', 'show_unimplemented_gui'):
            toolbar.addAction(view_about_view)

        # Set MainWindow properties
        app_title = 'Sane Subscription Feed'
        version = self.determine_version()
        if version:
            app_title += " v{}".format(version)
        self.setWindowTitle(app_title)
        self.setWindowIcon(QIcon(os.path.join(ICO_PATH, 'yubbtubbz-padding.ico')))
        self.statusBar().showMessage('Ready.')

        progress_bar = self.main_model.new_status_bar_progress(self)
        progress_bar.setFixedHeight(20)
        progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(progress_bar)

        # # Set a default view and layout
        # window_layout = QVBoxLayout()
        # self.view_grid()
        # self.setLayout(window_layout)

        # Display the window
        self.central_widget.addWidget(self.grid_view)
        self.central_widget.addWidget(self.play_view)
        self.central_widget.addWidget(self.list_detailed_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.central_widget.addWidget(self.list_tiled_view)
        self.central_widget.addWidget(self.subs_view)
        self.central_widget.addWidget(self.config_view)
        if read_config('Debug', 'show_unimplemented_gui'):
            self.central_widget.addWidget(self.about_view)
        self.central_widget.setCurrentWidget(self.grid_view)

        # if self.dimensions:
        #     self.resize(self.dimensions[0], self.dimensions[1])

    # Qt Overrides
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Control:
            # self.logger.debug("ctrl pressed")
            self.hotkey_ctrl_down = True

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Control:
            # self.logger.debug("ctrl released")
            self.hotkey_ctrl_down = False

    # Internal
    def determine_version(self):
        """
        Attempt to determine current release version based on VERSION.txt (and git)
        :return:
        """
        version_str = None
        git_branchtag = self.get_git_tag()
        try:
            with open(os.path.join(OS_PATH, '..', '..', 'VERSION'), 'r') as version_file:
                version = version_file.readline()
                if git_branchtag:
                    version_str = "{} [{}]".format(str(version), git_branchtag)
                else:
                    version_str = str(version)
        except:  # FIXME: PEP8 -- Too broad except clause
            pass

        return version_str

    def get_git_tag(self):
        """
        Gets git branch/commit_tag if in a git environment
        :return:
        """
        branchtag = None
        try:
            branchtag = check_output("git rev-parse --abbrev-ref HEAD", shell=True).decode("UTF-8").strip('\n') + ' / '
        except:  # FIXME: PEP8 -- Too broad except clause
            pass
        try:
            branchtag += check_output("git log -n 1 --pretty=format:%h", shell=True).decode("UTF-8").strip('\n')
        except:  # FIXME: PEP8 -- Too broad except clause
            pass

        return branchtag

    # Menu handling
    def add_menu(self, menubar, name):
        """
        Adds a menu and an optional amount of submenus
        :param menubar:
        :param name:
        :return:
        """
        self.menus[name] = menubar.addMenu(name)

    def add_submenu(self, menu, name, action, shortcut=None, tooltip=None, icon=None):
        """
        Adds a submenu with optional properties to a menu
        :param name:
        :param icon: icon filename (with relative path)
        :param tooltip: String
        :param action: Function
        :param shortcut: String on the form of '<key>+...n+key>' e.g. 'Ctrl+1'
        :param menu:
        :return:
        """
        if icon:
            this_icon = QIcon(os.path.join(ICO_PATH, icon))
            submenu = QAction(this_icon, name, self)
        else:
            submenu = QAction(name, self)
        if shortcut:
            submenu.setShortcut(shortcut)
        if tooltip:
            submenu.setStatusTip(tooltip)

        submenu.triggered.connect(action)
        if menu in self.menus:
            self.menus[menu].addAction(submenu)
        else:
            raise ValueError("add_submenu('{}', '{}', ...) ERROR: '{}' not in menus dict!".format(menu, name, menu))
        return submenu  # FIXME: Used by toolbar to avoid redefining items

    @staticmethod
    def hide_widget(widget):  # TODO: Deferred usage (Garbage collection issue)
        """
        Hides a widget/view
        :param widget:
        :return:
        """
        widget.setHidden(True)

    def view_grid(self):
        """
        Set View variable and CentralWidget to GridView
        :return:
        """
        # FIXME: hotfix for actions using self.grid_view(refresh and copy urls)
        self.central_widget.setCurrentWidget(self.grid_view)

    def view_play(self):
        """
        Set View variable and CentralWidget to GridView
        :return:
        """
        # FIXME: hotfix for actions using self.grid_view(refresh and copy urls)
        self.central_widget.setCurrentWidget(self.play_view)

    def view_subs(self):
        """
        Set View variable and CentralWidget to SubscriptionsView
        :return:
        """
        self.central_widget.setCurrentWidget(self.subs_view)

    def view_list_detailed(self):
        """
        Set View variable and CentralWidget to ListDetailedView
        :return:
        """
        self.central_widget.setCurrentWidget(self.list_detailed_view)

    def view_list_tiled(self):
        """
        Set View variable and CentralWidget to ListTiledView
        :return:
        """
        self.central_widget.setCurrentWidget(self.list_tiled_view)

    def view_config(self):
        """
        Set View variable and CentralWidget to ConfigView
        :return:
        """
        self.central_widget.setCurrentWidget(self.config_view)

    def view_about(self):
        """
        Set View variable and CentralWidget to AboutView
        :return:
        """
        self.central_widget.setCurrentWidget(self.about_view)

    # Function menu functions
    def clipboard_copy_urls(self):
        """
        Adds the url of each video in the view to a string, separated by newline and puts it on clipboard.
        :return:
        """
        grid_items = 20
        urls = ""
        for q_label in self.grid_view.q_labels:
            urls += "{}\n".format(q_label.video.url_video)

        self.logger.info("Copied URLs to clipboard: \n{}".format(urls))
        self.clipboard.setText(urls)
        self.statusBar().showMessage('Copied {} URLs to clipboard'.format(len(urls.splitlines())))

    def refresh_list(self):
        """
        Refresh the subscription feed
        :return:
        """
        self.main_model.main_window_listener.refreshVideos.emit(LISTENER_SIGNAL_NORMAL_REFRESH)

    def refresh_list_deep(self):
        """
        Refresh the subscription feed
        :return:
        """
        self.main_model.main_window_listener.refreshVideos.emit(LISTENER_SIGNAL_DEEP_REFRESH)

    def test_channels(self):
        """
        Sends a testChannels signal
        :return:
        """
        self.main_model.main_window_listener.testChannels.emit()

    def dir_search(self):
        """
        Sends a testChannels signal
        :return:
        """
        self.main_model.yt_dir_listener.manualCheck.emit()
        # do_walk(os.path.join("d:/", "youtube"))

    def db_reload(self):
        """
        Sends a testChannels signal
        :return:
        """
        self.main_model.grid_view_listener.updateFromDb.emit()

    def refresh_subs(self):
        """
        Fetch a new list of subscriptions
        :return:
        """
        self.main_model.main_window_listener.refreshSubs.emit()

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

    def timer_event(self, e):  # TODO: Unused, planned usage in future (progressbar auto-refresh-timer)
        """
        Runs a generic timer
        :param e:
        :return:
        """
        if self.step >= 100:
            self.timer.stop()
            self.btn.setText('Finished')
            return

        self.step = self.step + 1
        self.pbar.setValue(self.step)

    def timer_do_action(self):  # TODO: Unused, planned usage in future (progressbar auto-refresh-timer)
        """
        Tick that clock!
        :return:
        """
        if self.timer.isActive():
            self.timer.stop()
            self.btn.setText('Start')
        else:
            self.timer.start(100, self)
            self.btn.setText('Stop')

    def timer_progressbar(self):  # TODO: Unused, planned usage in future (progressbar auto-refresh-timer)
        """
        Progress, progress, progress!
        :return:
        """
        if self.timer.isActive():
            self.step = self.step + 1
            self.pbar.setValue(self.step)
            # self.timer.stop()
            self.btn.setText('0')
        else:
            # self.timer.start(100, self)
            self.btn.setText('1')

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
