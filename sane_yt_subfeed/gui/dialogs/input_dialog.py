from PyQt5.QtWidgets import QInputDialog, QDialog


class SaneInputDialog(QInputDialog):
    def __init__(self, sane_parent, main_window, action,  title=None, label=None, ok_button_text=None):
        super(QInputDialog, self).__init__(sane_parent)
        self.sane_parent = sane_parent
        self.main_window = main_window
        self.action = action
        if title:
            self.setWindowTitle(title)
        if label:
            self.setLabelText(label)
        if ok_button_text:
            self.setOkButtonText(ok_button_text)

        self.finished.connect(self.sane_finished)

    def sane_finished(self, ok):
        if ok:
            self.action(self.textValue())
