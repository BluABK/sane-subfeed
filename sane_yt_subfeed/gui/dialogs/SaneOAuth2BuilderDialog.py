from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QDialog

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.gui.dialogs.sane_input_dialog import SaneInputDialog

TITLE = 'Unnamed SaneOAuth2BuilderDialog'
TEXT = 'This is a SaneOAuth2BuilderDialog'
PLACEHOLDER = 'Enter text here..'
OK = 'OK'
CANCEL = 'Cancel'
WIDTH = 360
HEIGHT = 80
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
AUTH_PROVIDER_URL = "https://www.googleapis.com/oauth2/v1/certs"
REDIRECT_URIS = ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]


class SaneOAuth2BuilderDialog(QDialog):
    def __init__(self, parent, actions, title, text, ok_text, cancel_text, validator=None,
                 flags=Qt.WindowFlags, placeholder=PLACEHOLDER, use_placeholder=True):
        super(SaneOAuth2BuilderDialog, self).__init__(parent, flags())
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

    def init_ui(self):
        self.setWindowTitle(self.title)

        # Define contents
        if self.use_placeholder:
            self.input_box.setPlaceholderText(self.placeholder)
        self.input_box.setMinimumWidth(WIDTH)
        if self.validator:
            self.input_box.setValidator(self.validator)
            self.input_box.textChanged.connect(self.check_validator_state)
            self.input_box.textChanged.emit(self.input_box.text())
        self.cancel_button.setText(self.cancel_text)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.setText(self.ok_text)
        self.ok_button.clicked.connect(self.do_action)
        self.input_box.returnPressed.connect(self.do_action)

        # Define layouts
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        layout.addWidget(QLabel(self.text), 0, Qt.AlignCenter)
        layout.addWidget(self.input_box, 0, Qt.AlignCenter)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # self.resize(self.text.frameWidth(), 120)
        self.resize(WIDTH, HEIGHT)
