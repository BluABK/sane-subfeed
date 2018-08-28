from PyQt5.QtWidgets import QAction


class SaneToolBarAction(QAction):

    def __init__(self, parent, name, action, icon=None, **kwargs):
        if icon:
            super(SaneToolBarAction, self).__init__(icon, name, parent=parent)
        else:
            super(SaneToolBarAction, self).__init__(name, parent=parent)
        self.main_window = parent
        self.sane_kwargs = kwargs
        self.sane_action = action

        self.triggered.connect(self.perform_action)

    def perform_action(self):
        if self.sane_kwargs:
            self.sane_action(**self.sane_kwargs)
        else:
            self.sane_action()
