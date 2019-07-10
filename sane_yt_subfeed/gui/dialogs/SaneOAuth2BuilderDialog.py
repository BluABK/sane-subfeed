from PySide2.QtCore.Qt import Qt
from PySide2.QtWidgets import QPushButton, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QDialog

from sane_yt_subfeed import create_logger

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
    def __init__(self, parent, actions, title, text, ok_text, cancel_text=CANCEL, cancel_actions=None,
                 flags=Qt.WindowFlags, caller=None):
        """
        Builds a OAuth2 client secret JSON based on user input and known defaults,
        then calls action with the resulting json/dict as argument.

        :param parent:          Parent object to bind to.
        :param actions:         A function, or a list of functions to be called
        :param title:           Dialog title.
        :param text:            Dialog message body.
        :param ok_text:         Text on OK button.
        :param cancel_text:     Text on Cancel button.
        :param flags:           Qt WindowFlags.
        """
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

        if type(actions) is not list:
            self.action = actions
        else:
            self.action = None
            self.actions = actions

        self.caller = caller
        self.ok_text = ok_text
        self.cancel_text = cancel_text

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

        self.input_box_client_id = QLineEdit()
        self.input_box_project_id = QLineEdit()
        self.input_box_auth_uri = QLineEdit()
        self.input_box_token_uri = QLineEdit()
        self.input_box_auth_provider_url = QLineEdit()
        self.input_box_client_secret = QLineEdit()
        self.input_box_redirect_uris = QLineEdit()
        self.input_boxes = [self.input_box_client_id, self.input_box_project_id, self.input_box_auth_uri,
                            self.input_box_token_uri, self.input_box_auth_provider_url, self.input_box_client_secret,
                            self.input_box_redirect_uris]

        self.cancel_button = QPushButton(self)
        self.ok_button = QPushButton(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)

        # Define contents
        self.input_box_auth_uri.setText(AUTH_URI)
        self.input_box_auth_uri.setPlaceholderText(AUTH_URI)
        self.input_box_token_uri.setText(TOKEN_URI)
        self.input_box_token_uri.setPlaceholderText(TOKEN_URI)
        self.input_box_auth_provider_url.setText(AUTH_PROVIDER_URL)
        self.input_box_auth_provider_url.setPlaceholderText(AUTH_PROVIDER_URL)
        self.input_box_redirect_uris.setText(','.join(REDIRECT_URIS))
        self.input_box_redirect_uris.setPlaceholderText(','.join(REDIRECT_URIS))

        for input_box in self.input_boxes:
            input_box.setMinimumWidth(WIDTH)

        self.cancel_button.setText(self.cancel_text)
        if self.cancel_action is None and self.cancel_actions is None:
            self.cancel_button.clicked.connect(self.reject)
        else:
            self.cancel_button.clicked.connect(self.do_cancel_actions)
        self.ok_button.setText(self.ok_text)
        self.ok_button.clicked.connect(self.do_action)

        # Define layouts
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        button_layout = QHBoxLayout()
        row_layout_client_id = QHBoxLayout()
        row_layout_project_id = QHBoxLayout()
        row_layout_auth_uri = QHBoxLayout()
        row_layout_token_uri = QHBoxLayout()
        row_layout_auth_provider_url = QHBoxLayout()
        row_layout_client_secret = QHBoxLayout()
        row_layout_redirect_urls = QHBoxLayout()

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        layout.addWidget(QLabel(self.text), 0, Qt.AlignCenter)
        row_layout_client_id.addWidget(QLabel('Client ID'), 0, Qt.AlignLeft)
        row_layout_client_id.addWidget(self.input_box_client_id, 0, Qt.AlignRight)
        row_layout_project_id.addWidget(QLabel('Project ID'), 0, Qt.AlignLeft)
        row_layout_project_id.addWidget(self.input_box_project_id, 0, Qt.AlignRight)
        row_layout_auth_uri.addWidget(QLabel('Auth URI'), 0, Qt.AlignLeft)
        row_layout_auth_uri.addWidget(self.input_box_auth_uri, 0, Qt.AlignRight)
        row_layout_token_uri.addWidget(QLabel('Token URI'), 0, Qt.AlignLeft)
        row_layout_token_uri.addWidget(self.input_box_token_uri, 0, Qt.AlignRight)
        row_layout_auth_provider_url.addWidget(QLabel('Auth Provider URL'), 0, Qt.AlignLeft)
        row_layout_auth_provider_url.addWidget(self.input_box_auth_provider_url, 0, Qt.AlignRight)
        row_layout_client_secret.addWidget(QLabel('Client Secret'), 0, Qt.AlignLeft)
        row_layout_client_secret.addWidget(self.input_box_client_secret, 0, Qt.AlignRight)
        row_layout_redirect_urls.addWidget(QLabel('Redirect URLs'), 0, Qt.AlignLeft)
        row_layout_redirect_urls.addWidget(self.input_box_redirect_uris, 0, Qt.AlignRight)

        layout.addLayout(row_layout_client_id)
        layout.addLayout(row_layout_project_id)
        layout.addLayout(row_layout_auth_uri)
        layout.addLayout(row_layout_token_uri)
        layout.addLayout(row_layout_auth_provider_url)
        layout.addLayout(row_layout_client_secret)
        layout.addLayout(row_layout_redirect_urls)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # self.resize(self.text.frameWidth(), 120)
        self.resize(WIDTH, HEIGHT)

    def reset_values(self):
        for input_box in self.input_boxes:
            input_box.setText('')

    def do_action(self):
        client_secret_json = {
            'installed': {
                'client_id': self.input_box_client_id.text(),
                'project_id': self.input_box_project_id.text(),
                'auth_uri': self.input_box_auth_uri.text(),
                'token_uri': self.input_box_token_uri.text(),
                'auth_provider_x509_cert_url': self.input_box_auth_provider_url.text(),
                'client_secret': self.input_box_client_secret.text(),
                'redirect_uris': self.input_box_redirect_uris.text().split(',')}}
        self.action(client_secret_json)
        self.reset_values()

        # Close the dialog
        self.close()

    def do_cancel_action(self, action):
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

    def do_cancel_actions(self):
        """
        Executes do_action one or more times if CANCEL button is pressed.
        :return:
        """
        # Check if action is singular instead of plural (list).
        if self.cancel_action:
            self.do_cancel_action(self.cancel_action)
        else:
            for cancel_action in self.cancel_actions:
                self.do_cancel_action(cancel_action)

        # Close the dialog
        self.close()

