import time

from PyQt5.QtCore import pyqtSignal, QObject

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.database.db_category import DBCategory
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.write_operations import lock
from sane_yt_subfeed.gui.widgets.category_widget import CategoryWidget


class CategoryListener(QObject):
    static_self = None

    # Define signals
    add = pyqtSignal(CategoryWidget)
    remove = pyqtSignal(CategoryWidget)
    assign = pyqtSignal(list)           # [Category, Video].
    unassign = pyqtSignal(list)         # [Category, Video].
    rename = pyqtSignal(list)           # [Category, name].
    set_color = pyqtSignal(str)         # [Category, Color (hexadecimal)]
    enabled = pyqtSignal(bool)

    def __init__(self, main_model):
        super(CategoryListener, self).__init__()
        CategoryListener.static_self = self
        self.logger = create_logger(__name__ + ".CategoryListener")

        self.main_model = main_model

        # Connect signals to functions
        self.add.connect(self.new_category)
        self.remove.connect(self.remove_category)
        self.assign.connect(self.assign_category)
        self.unassign.connect(self.unassign_category)
        self.rename.connect(self.rename_category)
        self.set_color.connect(self.set_category_color)
        self.enabled.connect(self.set_category_enabled_status)

    def run(self):
        """
        Loop forever and listen to signals.
        :return:
        """
        while True:
            time.sleep(0.2)

    @staticmethod
    def new_category(category_widget: CategoryWidget):
        pass
        """
        Takes a Category object/QWidget which it uses to create a DBCategory Object,
        which is then written to DB.
        :param category_widget:
        :return:
        """
        lock.acquire()
        # FIXME: add check if already exists here.

        new_category_column = DBCategory(category_widget)
        db_session.add(new_category_column)
        db_session.commit()

        db_session.remove()
        lock.release()

    def remove_category(self, category_widget: CategoryWidget):
        pass

    def assign_category(self, category_widget: CategoryWidget, video):
        pass

    def unassign_category(self, category_widget: CategoryWidget, video):
        pass

    def rename_category(self, category_widget: CategoryWidget, new_name):
        pass

    def set_category_color(self, category_widget: CategoryWidget, color):
        pass

    def set_category_enabled_status(self, category_widget: CategoryWidget, boolean):
        pass

