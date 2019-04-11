import time

from PyQt5.QtCore import pyqtSignal

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.database.db_category import DBCategory


class CategoryListener:
    static_self = None

    # Define signals
    add = pyqtSignal(DBCategory)
    remove = pyqtSignal(DBCategory)
    assign = pyqtSignal(list)           # [Category, Video].
    unassign = pyqtSignal(list)         # [Category, Video].
    rename = pyqtSignal(str)            # New Category name.
    set_color = pyqtSignal(str)         # [Category, Color (hexadecimal)]
    enabled = pyqtSignal(bool)

    def __init__(self, main_model: MainModel):
        super(CategoryListener, self).__init__()
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

    def new_category(self, category):
        pass

    def remove_category(self, category):
        pass

    def assign_category(self, category, video):
        pass

    def unassign_category(self, category, video):
        pass

    def rename_category(self, category, new_name):
        pass

    def set_category_color(self, category, color):
        pass

    def set_category_enabled_status(self, category, boolean):
        pass

