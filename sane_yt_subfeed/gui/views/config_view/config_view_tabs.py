from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTabWidget

from sane_yt_subfeed.gui.views.config_view.config_scroll_area import ConfigScrollArea
from sane_yt_subfeed.gui.views.config_view.views.config_view import ConfigViewWidget

TAB_LIST = ["GUI", "Model", "Requests", "Thumbnails", "Threading", "Download", "Media player", "Default Application",
            "Logging", "Debug"]


class ConfigViewTabs(QTabWidget):

    def __init__(self, parent, icon: QIcon = None):
        super(ConfigViewTabs, self).__init__()
        self.sane_parent = parent
        if icon is not None:
            self.setWindowIcon(icon)
        self.setWindowTitle('Preferences')
        self.tabs = {}
        self.add_tabs(TAB_LIST)

    def add_tabs(self, tab_list):
        for tab_string in tab_list:
            new_tab = ConfigScrollArea(self)
            tab_widget = ConfigViewWidget(new_tab, self.sane_parent, tab_string)
            new_tab.set_view(tab_widget)
            self.tabs[tab_string] = new_tab
            self.addTab(new_tab, tab_string)
