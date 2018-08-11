from PyQt5.QtWidgets import QLineEdit

from sane_yt_subfeed.config_handler import read_config, set_config


class GenericLineEdit(QLineEdit):
    def __init__(self, parent, description, cfg_section, cfg_option, cfg_validator=None):
        super(QLineEdit, self).__init__(parent=parent)
        self.description = description
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option
        self.config_value = read_config(self.cfg_section, self.cfg_option, literal_eval=False)

        if cfg_validator:
            self.setValidator(cfg_validator)

        self.setPlaceholderText(self.config_value)

        self.returnPressed.connect(self.save_option)

    def save_option(self):
        set_config(self.cfg_section, self.cfg_option, self.text())
