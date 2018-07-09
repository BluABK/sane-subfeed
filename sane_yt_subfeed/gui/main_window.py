# !/usr/bin/python3
# -*- coding: utf-8 -*-

# std libs
import os

# PyQt5 libs
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QMenu, QVBoxLayout
from PyQt5.QtGui import QIcon

# Project internal libs
from sane_yt_subfeed.gui.views.subscriptions_view import SubscriptionsView
from sane_yt_subfeed.thumbnail_handler import thumbnails_dl_and_paths
from sane_yt_subfeed.uploads import Uploads
from sane_yt_subfeed.gui.views.grid_view import GridView

# Constants
OS_PATH = os.path.dirname(__file__)
ICO_PATH = os.path.join(OS_PATH, 'icons')


class MainWindow(QMainWindow):
    uploads = None
    current_view = None
    grid_view = None
    subs_view = None
    menus = None

    # noinspection PyArgumentList
    def __init__(self, dimensions=None, position=None):
        super().__init__()
        self.uploads = Uploads()
        self.clipboard = QApplication.clipboard()
        self.menus = {}
        if dimensions:
            self.dimensions = dimensions
        else:
            self.dimensions = [770, 700]
        self.position = position
        self.init_ui()

    def init_ui(self):
        # Define a menu and status bar
        menubar = self.menuBar()
        self.statusBar()

        # File menu
        self.add_menu(menubar, '&File')
        self.add_submenu('&File', 'Exit', qApp.quit, shortcut='Ctrl+Q', tooltip='Exit application')

        # Function menu
        self.add_menu(menubar, '&Function')

        # Set function menu triggers
        self.add_submenu('&Function', 'Copy all URLs', self.clipboard_copy_urls, shortcut='Ctrl+D',
                         tooltip='Copy URLs of all currently visible videos to clipboard')

        # refresh_list
        self.add_submenu('&Function', 'Refresh Feed', self.refresh_list, shortcut='Ctrl+R',
                         tooltip='Refresh the subscription feed')

        # View menu
        self.add_menu(menubar, '&View')
        view_grid_view = self.add_submenu('&View', 'Grid', self.view_grid, shortcut='Ctrl+1',
                                          tooltip='View subscription feed as a grid', icon='grid_blue.png')
        view_subs_view = self.add_submenu('&View', 'Subscriptions', self.view_subs, shortcut='Ctrl+2',
                                          tooltip='View Subscriptions', icon='subs.png')

        # Toolbar of different views
        toolbar = self.addToolBar('View')
        toolbar.addAction(view_grid_view)
        toolbar.addAction(view_subs_view)

        # Set MainWindow properties
        self.setWindowTitle('Sane-ish Subscription Feed')
        self.setWindowIcon(QIcon(os.path.join(ICO_PATH, 'blu.ico')))
        self.statusBar().showMessage('Ready.')
        if self.dimensions:
            self.resize(self.dimensions[0], self.dimensions[1])

        # Set a default view and layout
        window_layout = QVBoxLayout()
        self.view_subs()
        self.setLayout(window_layout)

        # Display the window
        self.show()

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

    # View handling
    def spawn_grid_view(self):
        """
        Creates a new GridView(QWidget) instance
        :return:
        """
        # self.grid_view = GridView(self.uploads, self.clipboard, self.statusBar())
        return GridView(self.uploads, self.clipboard, self.statusBar())

    def spawn_subs_view(self):
        """
        Creates a SubscriptionView(QWidget) instance
        :return:
        """
        # self.subs_view = SubscriptionsView(self.uploads, self.clipboard, self.statusBar())
        return SubscriptionsView(self.uploads, self.clipboard, self.statusBar())

    @staticmethod
    def hide_widget(widget):  # TODO: Deferred usage (Garbage collection issue)
        """
        Hides a widget/view
        :param widget:
        :return:
        """
        widget.setHidden(True)

    def switch_view_kindly(self, new_view):  # TODO: Deferred usage (Garbage collection issue)
        """
        Switch to a new view: Kind & Gentle edition.
        Hide currently shown view and show new_view instead
        :param new_view:
        :return:
        """
        self.hide_widget(self.current_view)
        if new_view.isHidden():
            new_view.setHidden(False)
        self.current_view = new_view
        self.setCentralWidget(new_view)
        self.update()

    def switch_view_destructively(self, new_view_spawn):
        """
        Switch to a new view: Destructive edition.
        Sets the current view and CentralWidget to a spawned new view, The old view then gets brutally murdered by
        PyQT5's ruthless garbage collection.
        :param new_view_spawn:
        :return:
        """
        self.current_view = new_view_spawn
        self.setCentralWidget(new_view_spawn)
        self.update()
        return new_view_spawn

    def view_grid(self):
        """
        Set View variable and CentralWidget
        Expected result: Set CentralWidget to GridView
        :return:
        """
        self.grid_view = self.switch_view_destructively(self.spawn_grid_view())

    def view_subs(self):
        """
        Set View variable and CentralWidget
        Expected result: Set CentralWidget to SubscriptionsView
        :return:
        """
        self.subs_view = self.switch_view_destructively(self.spawn_subs_view())

    # Function menu functions
    def clipboard_copy_urls(self):
        """
        Adds the url of each video in the view to a string, separated by newline and puts it on clipboard.
        :return:
        """
        grid_items = 20
        urls = ""
        for i in range(grid_items):
            urls += "{}\n".format(self.grid_view.uploads.uploads[i].url_video)

        print("Copied URLs to clipboard: \n{}".format(urls))
        self.clipboard.setText(urls)
        self.statusBar().showMessage('Copied {} URLs to clipboard'.format(len(urls.splitlines())))

    def refresh_list(self):
        """
        Reload the subscription feed items, and redraw the GridView
        :return:
        """
        self.grid_view.uploads.get_uploads()
        uploads = self.grid_view.uploads.uploads[:30]
        thumbnails_dl_and_paths(self.grid_view.uploads.uploads[:30])
        for q_label, video in zip(self.grid_view.q_labels, uploads):
            q_label.set_video(video)
            q_label.update()

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
