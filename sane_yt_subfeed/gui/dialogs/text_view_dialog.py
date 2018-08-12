from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLayout,
                            QPlainTextEdit, QPushButton, QSizePolicy,
                            QSpacerItem, QVBoxLayout)


class TextViewDialog(QDialog):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.text = text
        self.setupUi()

    def setupUi(self):
        self.resize(640, 480)
        self.verticalLayout = QVBoxLayout(self)
        self.textEdit = QPlainTextEdit(self)
        self.closeButton = QPushButton(self)
        self.copyButton = QPushButton(self)

        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.copyButton)
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.closeButton.clicked.connect(self.reject)

        self.closeButton.setText('Close')
        self.copyButton.setText('Copy to clipboard')
        self.textEdit.setPlainText(self.text)
        self.copyButton.clicked.connect(self.copy_text)

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.textEdit.toPlainText())