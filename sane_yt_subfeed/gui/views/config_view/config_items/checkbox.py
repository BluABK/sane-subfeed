from PyQt5.QtCore import Qt  # PyCharm bug: Anything from QtCore will fail detection, but it *is* there.
from PyQt5.QtWidgets import QCheckBox

from sane_yt_subfeed.config_handler import set_config


# ######################################################################## #
# ################################# [GUI] ################################ #
# ######################################################################## #

class GenericConfigCheckBox(QCheckBox):
    def __init__(self, parent, description, cfg_section, cfg_option, checked_actions=None, unchecked_actions=None,
                 checked_kwargs=None, unchecked_kwargs=None):
        """
        Generic Config Checkbox that can be checked or not checked. It also takes optional action functions.
        :param parent:
        :param description:
        :param cfg_section:
        :param cfg_option:
        :param checked_actions:   Functions to call when box gets checked. (can be list or single function)
        :param unchecked_actions: Functions to call when box gets unchecked. (can be list or single function)
        :param checked_kwargs    Keyword arguments (dict) to send in checked action calls. (can be list of kwargs)
        :param unchecked_kwargs  Keyword arguments (dict) to send in unchecked action calls. (can be list of kwargs)
        """
        super(QCheckBox, self).__init__(parent=parent)
        self.cfg_parent = parent
        self.description = description
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option
        self.checked_kwargs = checked_kwargs
        self.unchecked_kwargs = unchecked_kwargs
        self.checked_actions = checked_actions
        self.unchecked_actions = unchecked_actions

        self.setCheckState(2 if self.cfg_parent.input_read_config(cfg_section, cfg_option) else 0)

        self.stateChanged.connect(self.save_option)

    @staticmethod
    def do_actions(actions, kwargs):
        # There's Multiple actions
        if type(actions) is list:
            # There's separate kwargs for each action
            if type(kwargs) is list:
                for act, kwg in zip(actions, kwargs):
                    # There's a valid kwargs item
                    if kwg is not None:
                        act(**kwg)
                    else:
                        act()
            # There's shared kwargs for each action
            elif kwargs:
                for act in actions:
                    act(**kwargs)
            # There's no kwargs
            else:
                for act in actions:
                    act()

        # There's only one action
        elif actions:
            # There's kwargs
            if kwargs:
                actions(**kwargs)
            # There's no kwargs
            else:
                actions()

    def save_option(self, state):
        if state == Qt.Checked:
            set_config(self.cfg_section, self.cfg_option, 'True')
            self.do_actions(self.checked_actions, self.checked_kwargs)
        else:
            set_config(self.cfg_section, self.cfg_option, 'False')
            self.do_actions(self.unchecked_actions, self.unchecked_kwargs)
