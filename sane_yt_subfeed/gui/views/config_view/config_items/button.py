from PySide2.QtWidgets import QPushButton


# ######################################################################## #
# ################################# [GUI] ################################ #
# ######################################################################## #


class GenericConfigPushButton(QPushButton):
    def __init__(self, parent, name, description, cfg_section, cfg_option, tooltip=None, clear=False):
        super(QPushButton, self).__init__(parent=parent)
        if description:
            self.description = description
        if tooltip:
            self.setToolTip(tooltip)
        self.cfg_parent = parent
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option
        self.setText(name)

        if clear:
            self.clicked.connect(self.clear_option)
        else:
            self.clicked.connect(self.save_option)

    def save_option(self, value):
        self.cfg_parent.output_set_config(self.cfg_section, self.cfg_option, value)

    def clear_option(self):
        self.cfg_parent.output_set_config(self.cfg_section, self.cfg_option, "")
