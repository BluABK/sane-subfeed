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

        self.triggered.connect(self.sane_action)


    def set_qstyle(self, qstyle):
        self.main_window.set_theme(qstyle, stylesheet=False)
