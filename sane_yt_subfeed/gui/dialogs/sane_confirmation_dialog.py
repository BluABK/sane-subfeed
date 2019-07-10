from PySide2.QtCore.Qt import Qt
from PySide2.QtWidgets import QPushButton, QHBoxLayout, QLabel, QVBoxLayout, QDialog

from sane_yt_subfeed import create_logger

TITLE = 'Are you sure?'
TEXT = 'This is a SaneConfirmationDialog'
OK = 'OK'
CANCEL = 'Cancel'
WIDTH = 360
HEIGHT = 80


class SaneConfirmationDialog(QDialog):
    def __init__(self, parent, actions, title, text, ok_text, cancel_text,
                 cancel_actions=None, caller=None, flags=Qt.WindowFlags):
        """
        Prompts user for a Yes/No Confirmation where Yes results in a call for each action in actions

        :param parent:
        :param text: Text to display in dialog body.
        :param actions: A function, or a list of functions to be called
        :param caller: (If given) applies action to the caller function e.g. action(caller)
        :param title: Title of dialog window.
        :param ok_text: Text to display on OK button.
        :param cancel_text: Text to display on Cancel button.
        :param cancel_actions: Actions to perform on cancel/no, if None it will bind to reject.
        :param flags:
        """
        super(SaneConfirmationDialog, self).__init__(parent, flags())
        self.logger = create_logger(__name__)
        self.sane_parent = parent

        if not title:
            self.title = TITLE
        else:
            self.title = title
        if not text:
            self.text = TEXT
        else:
            self.text = text
        if not ok_text:
            self.ok_text = OK
        else:
            self.ok_text = ok_text
        if not cancel_text:
            self.cancel_text = CANCEL
        else:
            self.cancel_text = cancel_text

        if type(actions) is not list:
            self.action = actions
        else:
            self.action = None
            self.actions = actions

        if cancel_actions:
            if type(cancel_actions) is not list:
                self.cancel_action = cancel_actions
            else:
                self.cancel_action = None
                self.cancel_actions = cancel_actions
        # Required since cancel action is not guaranteed to exist
        else:
            self.cancel_action = None
            self.cancel_actions = None

        self.caller = caller
        self.cancel_button = QPushButton(self)
        self.ok_button = QPushButton(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)

        # Define contents
        self.cancel_button.setText(self.cancel_text)
        if self.cancel_action is None and self.cancel_actions is None:
            self.cancel_button.clicked.connect(self.reject)
        else:
            self.cancel_button.clicked.connect(self.do_cancel_actions)
        self.ok_button.setText(self.ok_text)
        self.ok_button.clicked.connect(self.do_ok_actions)

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

    def do_ok_actions(self):
        """
        Executes do_action one or more times if OK button is pressed.
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

    def do_cancel_actions(self):
        """
        Executes do_action one or more times if CANCEL button is pressed.
        :return:
        """
        # Check if action is singular instead of plural (list).
        if self.cancel_action:
            self.do_action(self.cancel_action)
        else:
            for cancel_action in self.cancel_actions:
                self.do_action(cancel_action)

        # Close the dialog
        self.close()
