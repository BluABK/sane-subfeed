from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton

from sane_yt_subfeed import create_logger

ICON = None
TITLE = 'Unnamed SaneDialog'
TEXT = 'This is a SaneDialog'
OK = 'OK'
WIDTH = 360
HEIGHT = 80
DEFAULT_ALIGNMENT = Qt.AlignCenter


class SaneDialog(QDialog):
    def __init__(self, parent, title, text, ok_text, alignment=DEFAULT_ALIGNMENT, flags=Qt.WindowFlags):
        super(SaneDialog, self).__init__(parent, flags())
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

        self.alignment = alignment

        self.ok_button = QPushButton(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)

        # Define contents
        self.ok_button.setText(self.ok_text)
        self.ok_button.clicked.connect(self.reject)

        # Define layouts
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.ok_button)

        layout.addWidget(QLabel(self.text), 0, Qt.AlignCenter)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.resize(WIDTH, HEIGHT)
