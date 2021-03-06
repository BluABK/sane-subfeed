from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPaintEvent, QPainter
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QFontDialog, QStyleOption, QStyle

from sane_yt_subfeed.gui.views.config_view.config_items.font_picker_button import FontPickerButton
from sane_yt_subfeed.handlers.config_handler import read_config, set_config
from sane_yt_subfeed.gui.views.config_view.config_items.button import GenericConfigPushButton
from sane_yt_subfeed.gui.views.config_view.config_items.checkbox import GenericConfigCheckBox
from sane_yt_subfeed.gui.views.config_view.config_items.combobox import GenericConfigComboBox
from sane_yt_subfeed.gui.views.config_view.config_items.line_edit import GenericLineEdit
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.constants import RESTART_REQUIRED_SIGNIFIER


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

    def paintEvent(self, paint_event: QPaintEvent):
        """
        Override painEvent in order to support stylesheets.
        :param paint_event:
        :return:
        """
        style_option = QStyleOption()
        style_option.initFrom(self)
        painter = QPainter(self)
        style = self.style()
        style.drawPrimitive(QStyle.PE_Widget, style_option, painter, self)

    def add_tab(self, tab, name):
        """
        Add a QWidget tab to the QTabWidget and add it to the tabs index dict
        :param tab:
        :param name:
        :return:
        """
        self.tabs.addTab(tab, name)
        self.tab_index[name] = tab

    def add_section(self, name):
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

    def add_option_checkbox(self, description, cfg_section, cfg_option, disabled=False, checked_actions=None,
                            unchecked_actions=None, checked_kwargs=None, unchecked_kwargs=None, restart_check=True):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param restart_check: If set to false, don't check if a restart (may) be required for this option.
        :param disabled: Sets disabled status if True.
        :param cfg_option:
        :param cfg_section:
        :param description:
        :param checked_actions:   Function to call when box gets checked.
        :param unchecked_actions: Function to call when box gets unchecked.
        :param checked_kwargs    Keyword arguments (dict) to send in checked action calls.
        :param unchecked_kwargs  Keyword arguments (dict) to send in unchecked action calls.
        :return:
        """
        if restart_check and checked_actions is None and unchecked_actions is None:
            description = "{} {}".format(description, RESTART_REQUIRED_SIGNIFIER)
        option = QLabel(description)
        value = GenericConfigCheckBox(self, description, cfg_section, cfg_option,
                                      checked_actions=checked_actions, unchecked_actions=unchecked_actions,
                                      checked_kwargs=checked_kwargs, unchecked_kwargs=unchecked_kwargs)
        if disabled:
            value.setDisabled(True)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_line_edit(self, description, cfg_section, cfg_option, cfg_validator=None, disabled=False,
                             actions=None, actions_kwargs=None, restart_check=True):
        """
        Add an option w/ text value to the ConfigView layout and increment the grid offset.
        :param restart_check: If set to false, don't check if a restart (may) be required for this option.
        :param disabled: Sets disabled status if True.
        :param cfg_validator:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :param actions:   Function to call when line gets edited.
        :param actions_kwargs:    Keyword arguments (dict) to send in checked action calls.
        :return:
        """
        if restart_check and actions is None:
            description = "{} {}".format(description, RESTART_REQUIRED_SIGNIFIER)
        option = QLabel(description)
        value = GenericLineEdit(self, description, cfg_section, cfg_option, cfg_validator=cfg_validator,
                                actions=actions, actions_kwargs=actions_kwargs)
        if disabled:
            value.setDisabled(True)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_fontpicker(self, description, cfg_section, cfg_option, disabled=False, tooltip=None,
                              actions=None, actions_kwargs=None, restart_check=True):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param description: Description of the option.
        :param cfg_section: Config section.
        :param cfg_option: Config option.
        :param disabled: Sets disabled status if True.
        :param tooltip: String to show on tooltip.
        :param actions: Function to call when font is selected.
        :param actions_kwargs: Keyword arguments (dict) to send in checked action calls.
        :param restart_check: If set to false, don't check if a restart (may) be required for this option.
        :return:
        """
        if restart_check and actions is None:
            description = "{} {}".format(description, RESTART_REQUIRED_SIGNIFIER)
        option = QLabel(description)
        value = FontPickerButton(self, cfg_section, cfg_option, tooltip=tooltip, actions=actions,
                                 actions_kwargs=actions_kwargs)

        if disabled:
            value.setDisabled(True)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

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

    def add_option_info(self, left_text, right_text):
        """
        Add flavourtext in the ConfigView option column and increment the grid offset.
        :param right_text: optional flavourtext
        :param left_text: optional flavourtext
        :return:
        """

        if left_text:
            self.layout.addWidget(QLabel(left_text), self.offset, 0)
        if right_text:
            self.layout.addWidget(QLabel(right_text), self.offset, 1)

        # Only increment offset if widgets were actually added
        self.offset += 1

    def add_option_info_restart_required(self):
        """
        Add Informaation about options that require application restart to take effect.
        :return:
        """
        desc = "Application restart is required for certain options to take effect."
        self.layout.addWidget(QLabel("{} {}".format(RESTART_REQUIRED_SIGNIFIER, desc), None), self.offset, 0)

        # Only increment offset if widgets were actually added
        self.offset += 1

    def add_option_combobox(self, description, cfg_section, cfg_option, items, restart_check=True, disabled=False):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param disabled:        Sets disabled status if True.
        :param restart_check:   If set to false, don't check if a restart (may) be required for this option.
        :param items:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """

        formated_items = [format(item) for item in items]

        if restart_check:
            description = "{} {}".format(description, RESTART_REQUIRED_SIGNIFIER)
        option = QLabel(description)
        value = GenericConfigComboBox(self, description, cfg_section, cfg_option, formated_items)
        if disabled:
            value.setDisabled(True)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_button(self, name, description, cfg_section, cfg_option, tooltip=None, clear=False,
                          restart_check=True):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param tooltip:
        :param restart_check: If set to false, don't check if a restart (may) be required for this option.
        :param name:
        :param clear:
        :param items:
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """
        if restart_check:
            description = "{} {}".format(description, RESTART_REQUIRED_SIGNIFIER)
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
