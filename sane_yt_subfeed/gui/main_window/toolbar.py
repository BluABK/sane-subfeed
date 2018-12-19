from PyQt5.QtWidgets import QToolBar, QActionGroup


class Toolbar(QToolBar):

    def __init__(self, parent):
        super(Toolbar, self).__init__(parent)
        self.action_group = None
        # self.actionTriggered.connect(self.select_action)

    # def select_action(self, selected_action):
    #     for action in self.actions():
    #         action.setChecked(False)
    #     selected_action.setChecked(True)
    #     for action in self.actions():
    #         print(action.isCheckable())

    # def set_checkable(self):
    #     for action in self.actions():
    #         action.setCheckable(True)

    def create_action_group(self):
        self.action_group = QActionGroup(self)
        for action in self.actions():
            action.setCheckable(True)
            self.action_group.addAction(action)
