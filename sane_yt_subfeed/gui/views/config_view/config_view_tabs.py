from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTabWidget

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.gui.views.config_view.config_scroll_area import ConfigScrollArea
from sane_yt_subfeed.gui.views.config_view.views.config_view import ConfigViewWidget

CONFIG_TABS = ["GUI", "Views", "Model", "Requests", "Thumbnails", "Threading", "Download", "Media player",
               "Default Application", "Logging", "Debug"]


class ConfigViewTabs(QTabWidget):

    def __init__(self, parent, icon: QIcon = None):
        super(ConfigViewTabs, self).__init__()
        self.sane_parent = parent
        self.logger = create_logger(__name__)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setWindowTitle('Preferences')
        self.tabs = {}
        self.add_tabs(CONFIG_TABS)

    def add_tab(self, tab: str):
        """
        Adds a ConfigScrollArea tab widget to the ConfigView.
        :param tab:
        :return:
        """
        if tab not in self.tabs.keys():
            new_csa_tab = ConfigScrollArea(self)
            tab_widget = ConfigViewWidget(new_csa_tab, self.sane_parent, tab)
            new_csa_tab.set_view(tab_widget)
            self.tabs[tab] = new_csa_tab
            self.addTab(new_csa_tab, tab)
        else:
            self.logger.error("Attempted to add already existing config tab: {}".format(tab))

    def del_tab(self, tab: str):
        """
        Removes a ConfigScrollArea tab widget from the ConfigView.
        :param tab:
        :return:
        """
        if tab in self.tabs.keys():
            self.removeTab(self.indexOf(self.tabs[tab]))
            self.tabs.pop(tab)
        else:
            self.logger.error("Attempted to delete non-existent config tab: {}".format(tab))

    def add_tabs(self, tabs: list):
        """
        Adds a ConfigScrollArea tab widgets to the ConfigView.
        :param tabs:
        :return:
        """
        for tab in tabs:
            if tab == 'Download' and not read_config('Play', 'enabled'):
                # Playback view and downloading capabilities are disabled, skip it.
                continue
            self.add_tab(tab)
