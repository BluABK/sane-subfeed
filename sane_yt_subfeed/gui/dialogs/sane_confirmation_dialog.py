from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QVBoxLayout, QDialog

from sane_yt_subfeed import create_logger

TITLE = 'Unnamed SaneConfirmationDialog'
TEXT = 'This is a SaneConfirmationDialog'
OK = 'OK'
CANCEL = 'Cancel'
WIDTH = 360
HEIGHT = 80


class SaneConfirmationDialog(QDialog):
    def __init__(self, parent, actions, caller=None, title=TITLE,
                 text=TEXT, ok_text=OK, cancel_text=CANCEL, flags=Qt.WindowFlags):
        """
        Prompts user for a Yes/No Confirmation where Yes results in a call for each action in actions

        :param parent:
        :param text: Text to display in dialog body.
        :param actions: A function, or a list of functions to be called
        :param caller: (If given) applies action to the caller function e.g. action(caller)
        :param title: Title of dialog window.
        :param ok_text: Text to display on OK button.
        :param cancel_text: Text to display on Cancel button.
        :param flags:
        """
        super(SaneConfirmationDialog, self).__init__(parent, flags())
        self.logger = create_logger(__name__)
        self.sane_parent = parent
        self.text = text
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        if type(actions) is not list:
            self.action = actions
        else:
            self.action = None
            self.actions = actions
        self.caller = caller
        self.title = title
        self.cancel_button = QPushButton(self)
        self.ok_button = QPushButton(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)

        # Define contents
        self.cancel_button.setText(self.cancel_text)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.setText(self.ok_text)
        self.ok_button.clicked.connect(self.do_actions)

        # Define layouts
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        layout.addWidget(QLabel(self.text), 0, Qt.AlignCenter)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.resize(WIDTH, HEIGHT)

    def do_action(self, action):
        """
        Executes an action.
        :param action:
        :return:
        """
        if self.caller:
            # Apply action on the object that called me.
            action(self.caller)
        else:
            # Do an action that doesn't depend on who called me.
            action()

        # Close the dialog
        self.close()

    def do_actions(self):
        """
        Executes do_action one or more times.
        :return:
        """
        # Check if action is singular instead of plural (list).
        if self.action:
            self.do_action(self.action)
        else:
            for action in self.actions:
                self.do_action(action)

        # Close the dialog
        self.close()
