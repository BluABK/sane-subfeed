from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QTabWidget, QVBoxLayout

from sane_yt_subfeed.gui.views.config_view.config_items.button import GenericConfigPushButton
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


        # Create tabs - Part 2: Set self layout and add tabs to it
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
        this_label = QLabel(name)
        this_label.setFont(QFont(self.section_fontfamily, self.section_fontsize, self.section_fontstyle))
        # this_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)    # Make section "centered" in GridView
        self.layout.addWidget(this_label, self.offset, 0)
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
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
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
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
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
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
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

        if left_text:
            self.layout.addWidget(QLabel(left_text), self.offset, 0)
        if right_text:
            self.layout.addWidget(QLabel(right_text), self.offset, 1)

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
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_button(self, name, description, cfg_section, cfg_option, tooltip=None, clear=False, tab_id=None):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param name:
        :param clear:
        :param tab_id:
        :param items:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """

        option = QLabel(description)
        value = GenericConfigPushButton(self, name, description, cfg_section, cfg_option, clear=clear, tooltip=tooltip)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def input_read_config_default(self, section, option):
        return "Not implemented"

    def input_read_config(self, section, option, literal_eval=True):
        return read_config(section, option, literal_eval=literal_eval)

    def output_set_config(self, section, option, value):
        set_config(section, option, value)
