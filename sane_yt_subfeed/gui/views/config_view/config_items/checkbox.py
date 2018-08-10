from PyQt5.QtCore import Qt  # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

from sane_yt_subfeed.config_handler import read_config, set_config, read_entire_config, get_sections, get_options


# ######################################################################## #
# ################################# [GUI] ################################ #
# ######################################################################## #

class GenericConfigCheckBox(QCheckBox):
    def __init__(self, parent, description, cfg_section, cfg_option):
        super(QCheckBox, self).__init__(parent=parent)
        self.description = description
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option

        self.setCheckState(2 if read_config(cfg_section, cfg_option) else 0)

        self.stateChanged.connect(self.change_this_plz_apply_button)

    def change_this_plz_apply_button(self, state):
        if state == Qt.Checked:
            set_config('Gui', 'launch_gui', 'True')
        else:
            set_config('Gui', 'launch_gui', 'False')
