from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QDialog

from sane_yt_subfeed import create_logger

TITLE = 'Unnamed SaneInputDialog'
TEXT = 'This is a SaneInputDialog'
OK = 'OK'
CANCEL = 'Cancel'
WIDTH = 360
HEIGHT = 120


class SaneInputDialog(QDialog):
    def __init__(self, parent, action, title=TITLE, text=TEXT, ok_text=OK, cancel_text=CANCEL, validator=None,
                 flags=Qt.WindowFlags):
        super(SaneInputDialog, self).__init__(parent, flags())
        self.logger = create_logger(__name__)
        self.sane_parent = parent
        self.text = text
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        self.action = action
        self.title = title
        self.input_box = QLineEdit()
        self.cancel_button = QPushButton(self)
        self.ok_button = QPushButton(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)

        # Define contents
        self.input_box.setPlaceholderText('Enter a YouTube URL here')
        self.input_box.setMinimumWidth(WIDTH)
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

    def do_action(self):
        print(self.input_box.text())
        self.action(self.input_box.text())
