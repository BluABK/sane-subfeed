from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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
        self.section_count = 0
        self.section_fontsize = 10
        self.section_fontfamily = "Helvetica"
        self.section_fontstyle = QFont.Black

        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
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
        self.tab_defaultapp = QWidget()
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
        self.add_tab(self.tab_defaultapp, "Default Application")
        self.add_tab(self.tab_logging, "Logging")
        self.add_tab(self.tab_debug, "Debug")

        # Create tabs - Part 1: Set layouts
        self.tab_gui.layout = QGridLayout()
        self.tab_gui.layout.setAlignment(Qt.AlignTop)
        self.tab_model.layout = QGridLayout()
        self.tab_model.layout.setAlignment(Qt.AlignTop)
        self.tab_requests.layout = QGridLayout()
        self.tab_requests.layout.setAlignment(Qt.AlignTop)
        self.tab_thumbnails.layout = QGridLayout()
        self.tab_thumbnails.layout.setAlignment(Qt.AlignTop)
        self.tab_threading.layout = QGridLayout()
        self.tab_threading.layout.setAlignment(Qt.AlignTop)
        self.tab_downloads.layout = QGridLayout()
        self.tab_downloads.layout.setAlignment(Qt.AlignTop)
        self.tab_mediaplayer.layout = QGridLayout()
        self.tab_mediaplayer.layout.setAlignment(Qt.AlignTop)
        self.tab_defaultapp.layout = QGridLayout()
        self.tab_defaultapp.layout.setAlignment(Qt.AlignTop)
        self.tab_logging.layout = QGridLayout()
        self.tab_logging.layout.setAlignment(Qt.AlignTop)
        self.tab_debug.layout = QGridLayout()
        self.tab_debug.layout.setAlignment(Qt.AlignTop)

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

    def set_tab_layouts(self):
        """
        Call this function *AFTER* having populated tabs
        :return:
        """
        for tab_id, tab in self.tab_index.items():
            self.logger.info("Setting tab layout for '{}' | {}".format(tab_id, tab.__dict__))
            tab.setLayout(tab.layout)

    def add_section(self, name, tab_id=None):
        """
        Add a section to the ConfigView layout and increment grid offset.
        :return:
        """
        if tab_id is None:
            this_label = QLabel(name)
            this_label.setFont(QFont(self.section_fontfamily, self.section_fontsize, self.section_fontstyle))
            # this_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)    # Make section "centered" in GridView
            self.layout.addWidget(this_label, self.offset, 0)
        else:
            this_label = QLabel(name)
            # this_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)    # Make section "centered" in GridView
            this_label.setFont(QFont(self.section_fontfamily, self.section_fontsize, self.section_fontstyle))
            self.tab_index[tab_id].layout.addWidget(this_label, self.offset, 0)
        self.section_count += 1
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

    def add_option_info(self, left_text, right_text, tab_id=None):
        """
        Add flavourtext in the ConfigView option column and increment the grid offset.
        :param right_text: optional flavourtext
        :param left_text: optional flavourtext
        :param tab_id:
        :return:
        """

        if tab_id is None:
            if left_text:
                self.layout.addWidget(QLabel(left_text), self.offset, 0)
            if right_text:
                self.layout.addWidget(QLabel(right_text), self.offset, 1)
        else:
            if left_text:
                self.tab_index[tab_id].layout.addWidget(QLabel(left_text), self.offset, 0)
            if right_text:
                self.tab_index[tab_id].layout.addWidget(QLabel(right_text), self.offset, 1)

        # Only increment offset if widgets were actually added
        # if left_text or right_text:
        self.offset += 1

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
