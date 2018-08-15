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

        self.base_icon = QPixmap(os.path.join(ICONS_PATH, 'database.png'))
        self.full_icon = self.base_icon.scaled(QSize(self.height(), self.height()), Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
        self.sane_painter = QPainter(self.full_icon)
        self.default_dot = QPixmap(os.path.join(ICONS_PATH, 'default_dot.png')).scaled(
            QSize(self.height() * 0.3, self.height() * 0.3), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.read_dot = QPixmap(os.path.join(ICONS_PATH, 'blue_dot.png')).scaled(
            QSize(self.height() * 0.3, self.height() * 0.3), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.write_dot = QPixmap(os.path.join(ICONS_PATH, 'green_dot.png')).scaled(
            QSize(self.height() * 0.3, self.height() * 0.3), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.draw_read_icon(self.default_dot)
        self.draw_write_icon(self.default_dot)

        self.setPixmap(self.full_icon)

        DatabaseListener.static_instance.dbStateChanged.connect(self.change_state)

    def draw_write_icon(self, pixmap):
        self.sane_painter.drawPixmap(self.full_icon.width() * 0.6, self.full_icon.height() * 0.6, pixmap)

    def draw_read_icon(self, pixmap):
        self.sane_painter.drawPixmap(self.full_icon.width() * 0.1, self.full_icon.height() * 0.6, pixmap)

    def change_state(self, state):
        if state == DatabaseListener.DB_STATE_READ_WRITE:
            self.logger.debug("Changing db state icon to read/write".format(state))
            self.draw_read_icon(self.read_dot)
            self.draw_write_icon(self.write_dot)
        elif state == DatabaseListener.DB_STATE_WRITE:
            self.logger.debug("Changing db state icon to write".format(state))
            self.draw_read_icon(self.default_dot)
            self.draw_write_icon(self.write_dot)
        elif state == DatabaseListener.DB_STATE_READ:
            self.logger.debug("Changing db state icon to read".format(state))
            self.draw_read_icon(self.read_dot)
            self.draw_write_icon(self.default_dot)
        else:
            self.logger.debug("Changing db state icon to idle".format(state))
            self.draw_read_icon(self.default_dot)
            self.draw_write_icon(self.default_dot)
        self.setPixmap(self.full_icon)

