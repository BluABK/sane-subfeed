from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.controller.listeners.gui.category_listener import CategoryListener
from sane_yt_subfeed.gui.widgets.category_widget import CategoryWidget


class CategoryManagerView(QWidget):

    def __init__(self, parent):
        super(CategoryManagerView, self).__init__(parent)
        self.logger = create_logger(__name__)
        self.root = parent  # MainWindow
        self.parent = parent
        self.category_listener = self.root.main_model.category_listener

        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar
        self.row = 0
        self.init_ui()

    def init_ui(self):
        self.logger.info("Initializing UI: CategoryManagerView")
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setVerticalSpacing(0)
        dummy_cat1 = self.add_category("Testing 1")
        dummy_cat2 = self.add_category("Testing 2")
        dummy_cat3 = self.add_category("Testing 3")
        dummy_cat4 = self.add_category("Testing long name")

        self.add_category_mgmt_row(dummy_cat1, layout)
        self.add_category_mgmt_row(dummy_cat2, layout)
        self.add_category_mgmt_row(dummy_cat3, layout)
        self.add_category_mgmt_row(dummy_cat4, layout)

        self.setLayout(layout)

    def add_category(self, name):
        widget = CategoryWidget(self, name, self.category_listener)
        CategoryListener.static_self.add.emit(widget)
        return widget

    def add_category_mgmt_row(self, category, layout, alignment=Qt.AlignLeft):
        del_cat_button = QPushButton("Delete", self)
        del_cat_button.clicked.connect(category.remove)
        rename_cat_button = QPushButton("Rename", self)
        rename_cat_button.clicked.connect(category.rename)

        layout.addWidget(category, self.row, 0, alignment)
        layout.addWidget(del_cat_button, self.row, 0, alignment)
        layout.addWidget(rename_cat_button, self.row, 0, alignment)

