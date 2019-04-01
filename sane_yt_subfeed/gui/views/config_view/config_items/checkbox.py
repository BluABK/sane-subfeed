from PyQt5.QtCore import Qt  # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QCheckBox

from sane_yt_subfeed.config_handler import set_config


# ######################################################################## #
# ################################# [GUI] ################################ #
# ######################################################################## #

class GenericConfigCheckBox(QCheckBox):
    def __init__(self, parent, description, cfg_section, cfg_option, checked_action=None, unchecked_action=None,
                 checked_kwargs=None, unchecked_kwargs=None):
        """
        Generic Config Checkbox that can be checked or not checked. It also takes optional action functions.
        :param parent:
        :param description:
        :param cfg_section:
        :param cfg_option:
        :param checked_action:   Function to call when box gets checked.
        :param unchecked_action: Function to call when box gets unchecked.
        :param checked_kwargs    Keyword arguments (dict) to send in checked action calls.
        :param unchecked_kwargs  Keyword arguments (dict) to send in unchecked action calls.
        """
        super(QCheckBox, self).__init__(parent=parent)
        self.cfg_parent = parent
        self.description = description
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option
        self.checked_kwargs = checked_kwargs
        self.unchecked_kwargs = unchecked_kwargs
        if checked_action:
            self.checked_action = checked_action
        if unchecked_action:
            self.unchecked_action = unchecked_action

        self.setCheckState(2 if self.cfg_parent.input_read_config(cfg_section, cfg_option) else 0)

        self.stateChanged.connect(self.save_option)

    def save_option(self, state):
        if state == Qt.Checked:
            set_config(self.cfg_section, self.cfg_option, 'True')
            if self.checked_action:
                if self.checked_kwargs:
                    self.checked_action(**self.checked_kwargs)
                else:
                    self.checked_action()
        else:
            set_config(self.cfg_section, self.cfg_option, 'False')
            if self.unchecked_action:
                if self.unchecked_kwargs:
                    self.unchecked_action(**self.unchecked_kwargs)
                else:
                    self.unchecked_action()
