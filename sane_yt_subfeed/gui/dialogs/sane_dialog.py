from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

from sane_yt_subfeed import create_logger


TITLE = 'Unnamed SaneDialog'
TEXT = 'This is a SaneDialog'
DEFAULT_ALIGNMENT = Qt.AlignCenter


class SaneDialog(QDialog):
    def __init__(self, parent, title=TITLE, text=TEXT, alignment=DEFAULT_ALIGNMENT, flags=Qt.WindowFlags):
        super().__init__(parent, flags())
        self.logger = create_logger(__name__)
        self.title = title
        self.text = QLabel(text, self)
        self.alignment = alignment
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)

        # Define layout
        layout = QVBoxLayout()

        # Add content to layout
        layout.addWidget(self.text, 0, self.alignment)

        # Apply the layout
        self.setLayout(layout)

        # FIXME: Resize width to len of info text string
        self.resize(360, 120)

