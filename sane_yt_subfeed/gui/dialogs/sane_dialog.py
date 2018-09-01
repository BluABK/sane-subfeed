from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

from sane_yt_subfeed import create_logger

OK = 'Ok'
CANCEL = 'Cancel'


class SaneDialog(QDialog):
    def __init__(self, parent, text, ok_text=OK, cancel_text=CANCEL):
        super().__init__(parent)
        self.logger = create_logger(__name__)
        self.text = text
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.cancel_button = QPushButton(self)
        self.ok_button = QPushButton(self)
        self.init_ui()

    def init_ui(self):
        # FIXME: Resize width to len of info text string
        self.resize(360, 120)
        self.logger.warn("Unimplemented SaneDialog")
        self.layout.addWidget(QLabel(self.text))
        self.layout.addWidget(self.input_box)
        self.layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

        self.input_box.setInputMask('Enter text here')
        self.cancel_button.setText(self.cancel_text)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.setText(self.ok_text)
        # self.ok_button.clicked.connect()

