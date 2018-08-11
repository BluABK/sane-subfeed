from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

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
        self.setLayout(self.layout)



    def add_section(self, name):
        """
        Add a section to the ConfigView layout and increment grid offset.
        :return:
        """
        self.layout.addWidget(QLabel(name), self.offset, 0)
        self.offset += 1

    def add_option_checkbox(self, description, cfg_section, cfg_option):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
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

    def add_option_line_edit(self, description, cfg_section, cfg_option, cfg_validator=None):
        """
        Add an option w/ text value to the ConfigView layout and increment the grid offset.
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

    def add_option_inactive(self, description, cfg_section, cfg_option):
        """
        Add an option w/ UNEDITABLE value to the ConfigView layout and increment the grid offset.
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

    def add_option_combobox(self, description, cfg_section, cfg_option, items):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
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

    def input_read_config_default(self, section, option):
        return "Not implemented"

    def input_read_config(self, section, option, literal_eval=False):
        return read_config(section, option, literal_eval=literal_eval)

    def output_set_config(self, section, option, value):
        set_config(section, option, value)