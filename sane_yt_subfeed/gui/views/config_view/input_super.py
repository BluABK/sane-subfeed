from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QTabWidget, QVBoxLayout

from sane_yt_subfeed.gui.views.config_view.config_items.checkbox import GenericConfigCheckBox
from sane_yt_subfeed.gui.views.config_view.config_items.combobox import GenericConfigComboBox
from sane_yt_subfeed.gui.views.config_view.config_items.line_edit import GenericLineEdit
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.config_handler import DEFAULTS, read_config, set_config


class InputSuper(QWidget):
    """
    Configuration widget
    """

    def __init__(self, parent, root):
        """
        A GUI Widget that reads and sets config.ini settings
        :param parent:
        :param clipboard:
        :param status_bar:
        """
        super(InputSuper, self).__init__(parent)
        self.parent = parent
        self.root = root  # MainWindow
        self.logger = create_logger(__name__)
        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar
        self.offset = 0

        self.layout = QGridLayout()
        # self.layout = QVBoxLayout()

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab_index = {}
        self.tab_gui = QWidget()
        self.tab_model = QWidget()
        self.tab_requests = QWidget()
        self.tab_thumbnails = QWidget()
        self.tab_threading = QWidget()
        self.tab_downloads = QWidget()
        self.tab_mediaplayer = QWidget()
        self.tab_logging = QWidget()
        self.tab_debug = QWidget()

        # Add tabs
        self.add_tab(self.tab_gui, "GUI")
        self.add_tab(self.tab_model, "Model")
        self.add_tab(self.tab_requests, "Requests")
        self.add_tab(self.tab_thumbnails, "Thumbnails")
        self.add_tab(self.tab_threading, "Threading")
        self.add_tab(self.tab_downloads, "Download")
        self.add_tab(self.tab_mediaplayer, "Media player")
        self.add_tab(self.tab_logging, "Logging")
        self.add_tab(self.tab_debug, "Debug")

        # Create tabs - Part 1: Set layouts
        self.tab_gui.layout = QGridLayout()
        self.tab_model.layout = QGridLayout()
        self.tab_requests.layout = QGridLayout()
        self.tab_thumbnails.layout = QGridLayout()
        self.tab_threading.layout = QGridLayout()
        self.tab_downloads.layout = QGridLayout()
        self.tab_mediaplayer.layout = QGridLayout()
        self.tab_logging.layout = QGridLayout()
        self.tab_debug.layout = QGridLayout()

        # Create tabs - Part 2: Set self layout and add tabs to it
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def add_tab(self, tab, name):
        """
        Add a QWidget tab to the QTabWidget and add it to the tabs index dict
        :param tab:
        :param name:
        :return:
        """
        self.tabs.addTab(tab, name)
        self.tab_index[name] = tab

    def add_section(self, name, tab_id=None):
        """
        Add a section to the ConfigView layout and increment grid offset.
        :return:
        """
        if tab_id is None:
            self.layout.addWidget(QLabel(name), self.offset, 0)
        else:
            self.tab_index[tab_id].layout.addWidget(QLabel(name), self.offset, 0)
        self.offset += 1

    def add_option_checkbox(self, description, cfg_section, cfg_option, tab_id=None):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param tab_id:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = GenericConfigCheckBox(self, description, cfg_section, cfg_option)
        if tab_id is None:
            self.layout.addWidget(option, self.offset, 0)
            self.layout.addWidget(value, self.offset, 1)
        else:
            self.tab_index[tab_id].layout.addWidget(option, self.offset, 0)
            self.tab_index[tab_id].layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_line_edit(self, description, cfg_section, cfg_option, cfg_validator=None, tab_id=None):
        """
        Add an option w/ text value to the ConfigView layout and increment the grid offset.
        :param cfg_validator:
        :param tab_id:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = GenericLineEdit(self, description, cfg_section, cfg_option, cfg_validator=cfg_validator)
        if tab_id is None:
            self.layout.addWidget(option, self.offset, 0)
            self.layout.addWidget(value, self.offset, 1)
        else:
            self.tab_index[tab_id].layout.addWidget(option, self.offset, 0)
            self.tab_index[tab_id].layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_inactive(self, description, cfg_section, cfg_option, tab_id=None):
        """
        Add an option w/ UNEDITABLE value to the ConfigView layout and increment the grid offset.
        :param tab_id:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = QLabel(self.input_read_config_default(cfg_section, cfg_option))
        if tab_id is None:
            self.layout.addWidget(option, self.offset, 0)
            self.layout.addWidget(value, self.offset, 1)
        else:
            self.tab_index[tab_id].layout.addWidget(option, self.offset, 0)
            self.tab_index[tab_id].layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_combobox(self, description, cfg_section, cfg_option, items, tab_id=None):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param tab_id:
        :param items:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """

        formated_items = [format(item) for item in items]

        option = QLabel(description)
        value = GenericConfigComboBox(self, description, cfg_section, cfg_option, formated_items)
        if tab_id is None:
            self.layout.addWidget(option, self.offset, 0)
            self.layout.addWidget(value, self.offset, 1)
        else:
            self.tab_index[tab_id].layout.addWidget(option, self.offset, 0)
            self.tab_index[tab_id].layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def input_read_config_default(self, section, option):
        return "Not implemented"

    def input_read_config(self, section, option, literal_eval=True):
        return read_config(section, option, literal_eval=literal_eval)

    def output_set_config(self, section, option, value):
        set_config(section, option, value)
