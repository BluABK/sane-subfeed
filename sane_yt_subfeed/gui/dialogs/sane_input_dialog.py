from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QDialog

from sane_yt_subfeed import create_logger

TITLE = 'Unnamed SaneInputDialog'
TEXT = 'This is a SaneInputDialog'
PLACEHOLDER = 'Enter text here..'
OK = 'OK'
CANCEL = 'Cancel'
WIDTH = 360
HEIGHT = 80


class SaneInputDialog(QDialog):
    def __init__(self, parent, action, title=TITLE, text=TEXT, ok_text=OK, cancel_text=CANCEL, validator=None,
                 flags=Qt.WindowFlags, placeholder=PLACEHOLDER, use_placeholder=True, init_ui=True):
        """
        Text input dialog box that does an action on the text input.

        :param parent:          Parent object to bind to.
        :param action:          Action to perform on OK/Enter.
        :param title:           Dialog title.
        :param text:            Dialog message body.
        :param ok_text:         Text on OK button.
        :param cancel_text:     Text on Cancel button.
        :param validator:       If set, use a validator on the input field.
        :param flags:           Qt WindowFlags.
        :param placeholder:     Placeholder text in text input field.
        :param use_placeholder: Whether or not to use a placeholder text.
        :param init_ui:         Whether or not to init ui (Usually only False if
                                inherited by a class with its own init_ui().
        """
        super(SaneInputDialog, self).__init__(parent, flags())
        self.logger = create_logger(__name__)
        self.sane_parent = parent
        self.text = text
        self.placeholder = placeholder
        self.use_placeholder = use_placeholder
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        self.action = action
        self.title = title
        self.input_box = QLineEdit()
        self.validator = validator
        self.cancel_button = QPushButton(self)
        self.ok_button = QPushButton(self)

        if init_ui:
            self.init_ui()

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

    def reset_values(self):
        self.input_box.setText('')
        if self.use_placeholder:
            self.input_box.setPlaceholderText(self.placeholder)

    def do_action(self):
        if self.validator:
            if self.validator.validate(self.input_box.text(), 0)[0] == QValidator.Acceptable:
                self.action(self.input_box.text())
                self.reset_values()
            else:
                self.logger.debug("User attempted action but QValidator did not deem input acceptable: {}".format(
                    self.input_box.text()))
        else:
            self.action(self.input_box.text())
            self.reset_values()

    def check_validator_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QValidator.Intermediate:
            # color = '#fff79a' # yellow
            color = '#ffffff'
        else:
            color = '#f6989d'  # red

        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
