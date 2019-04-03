from PyQt5.QtWidgets import QLineEdit


class GenericLineEdit(QLineEdit):
    def __init__(self, parent, description, cfg_section, cfg_option, cfg_validator=None, actions=None,
                 actions_kwargs=None):
        super(QLineEdit, self).__init__(parent=parent)
        self.description = description
        self.cfg_parent = parent
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option
        self.actions = actions
        self.actions_kwargs = actions_kwargs

        self.config_value = self.cfg_parent.input_read_config(self.cfg_section, self.cfg_option, literal_eval=False)

        if cfg_validator:
            self.setValidator(cfg_validator)

        self.setPlaceholderText(self.config_value)
        self.setText(self.config_value)

        self.textEdited.connect(self.save_option)

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

    def save_option(self):
        self.cfg_parent.output_set_config(self.cfg_section, self.cfg_option, self.text())
        self.do_actions(self.actions, self.actions_kwargs)
