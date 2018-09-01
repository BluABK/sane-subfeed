from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel

from sane_yt_subfeed import create_logger

ICON = None
TITLE = 'Unnamed SaneDialog'
TEXT = 'This is a SaneDialog'
DEFAULT_ALIGNMENT = Qt.AlignCenter


class SaneDialog(QDialog):  # FIXME: FUTURE: Was meant to be inherited, but might be useful on its own in future
    def __init__(self, parent, title=TITLE, text=TEXT, alignment=DEFAULT_ALIGNMENT, flags=Qt.WindowFlags):
        super().__init__(parent, flags())
        self.logger = create_logger(__name__)
        self.title = title
        self.setWindowTitle(self.title)
        self.text = QLabel(text, self)
        self.alignment = alignment

