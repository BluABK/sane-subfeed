from PyQt5.QtWidgets import QInputDialog, QDialog


class SaneInputDialog(QInputDialog):
    def __init__(self, sane_parent, main_winodw,  title=None, label=None, ok_button_text=None):
        super(QInputDialog, self).__init__(sane_parent)
        self.sane_parent = sane_parent
        self.main_window = main_winodw
        if title:
            self.setWindowTitle(title)
        if label:
            self.setLabelText(label)
        if ok_button_text:
            self.setOkButtonText(ok_button_text)

        self.finished.connect(self.sane_finished)

    def sane_finished(self, ok):
        if ok:
            self.main_window.get_single_video(self.textValue())