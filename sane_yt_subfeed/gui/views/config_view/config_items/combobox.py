from PyQt5.QtWidgets import QComboBox

from sane_yt_subfeed.config_handler import read_config, set_config

   # FIXME: Get QComboBox to set strings not ints
tt_font_sizes = ['h1', 'h2', 'h3', 'h4', 'h5', 'p']


# ######################################################################## #
# ################################# [GUI] ################################ #
# ######################################################################## #


class GenericConfigComboBox(QComboBox):
    def __init__(self, parent, description, cfg_section, cfg_option, items):
        super(QComboBox, self).__init__(parent=parent)
        self.description = description
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option
        self.items = items

        self.addItems(self.items)
        current_item = read_config(cfg_section, cfg_option, literal_eval=False)
        for index in range(0, len(self.items)):
            if self.itemText(index) == current_item:
                self.setCurrentIndex(index)
                break

        self.currentIndexChanged.connect(self.save_option)

    def save_option(self, value):
        set_config(self.cfg_section, self.cfg_option, format(self.itemText(value)))


