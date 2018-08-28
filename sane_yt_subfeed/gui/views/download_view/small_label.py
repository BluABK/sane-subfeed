from PyQt5.QtWidgets import QLabel, QSizePolicy


class SmallLabel(QLabel):
    def __init__(self, text, parent, *__args):
        super(SmallLabel, self).__init__(*__args, parent=parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setText(text)
