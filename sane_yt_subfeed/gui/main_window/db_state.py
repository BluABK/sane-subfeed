import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QLabel

from sane_yt_subfeed.absolute_paths import ICONS_PATH
from sane_yt_subfeed.log_handler import create_logger

from sane_yt_subfeed.controller.database_listener import DatabaseListener


class DbStateIcon(QLabel):
    def __init__(self, sane_parent, main_model):
        super(DbStateIcon, self).__init__(parent=sane_parent)
        self.logger = create_logger(__name__)
        self.sane_parent = sane_parent
        self.main_model = main_model
        DatabaseListener.static_instance.dbStateChanged.connect(self.change_state)
        self.change_state(DatabaseListener.DB_STATE_IDLE)

    def change_state(self, state):
        if self.isHidden():
            self.show()
        if state == DatabaseListener.DB_STATE_READ_WRITE:
            self.logger.debug("Changing db state icon to read/write".format(state))
            self.setText("read/write")
        elif state == DatabaseListener.DB_STATE_WRITE:
            self.logger.debug("Changing db state icon to write".format(state))
            self.change_icon(os.path.join(ICONS_PATH, 'database.png'))
        elif state == DatabaseListener.DB_STATE_READ:
            self.logger.debug("Changing db state icon to read".format(state))
            self.setText("read")
        else:
            self.logger.debug("Changing db state icon to idle".format(state))
            self.hide()
        self.update()

    def change_icon(self, icon_path):
        full_icon = QPixmap(icon_path)
        scaled_icon = full_icon.scaled(QSize(self.height(), self.height()), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_icon)
        # painter = QPainter(self)
        # painter.drawPixmap(0, 0, p)
