import time

from PySide2.QtCore import QObject, SIGNAL
from PySide2.QtCore.Qt import Qt
from PySide2.QtGui import QPalette

from sane_yt_subfeed.handlers.log_handler import create_logger


class ProgressBarListener(QObject):
    setMaximum = SIGNAL(int)
    setProgress = SIGNAL(int)
    updateProgress = SIGNAL()
    setText = SIGNAL(str)
    resetBar = SIGNAL()
    progress_bar = None

    def __init__(self, model, progress_bar):
        super().__init__()
        self.model = model
        self.progress_bar = progress_bar
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.setMaximum.connect(self.set_maximum)
        self.setProgress.connect(self.set_progress)
        self.updateProgress.connect(self.update_progress)
        self.setText.connect(self.set_text)
        self.resetBar.connect(self.reset_bar)
        self.logger = create_logger(__name__ + '.ProgressBarListener')

    def run(self):
        while True:
            time.sleep(2)

    def set_color(self, color):
        palette = QPalette(self.palette())
        palette.setColor(QPalette.Highlight, color)
        self.setPalette(palette)

    def reset_palette(self):
        self.setPalette(self.default_palette)

    def pause(self):
        self.set_color(Qt.darkYellow)

    def resume(self):
        self.reset_palette()

    def finish(self):
        self.set_color(Qt.darkGreen)

    def fail(self):
        self.set_color(Qt.darkRed)

    def set_maximum(self, max):
        self.progress_bar.setMaximum(max)

    def set_progress(self, progress):
        self.progress_bar.setValue(progress)
        self.progress_bar.update()

    def update_progress(self):
        value = self.progress_bar.value()
        self.progress_bar.setValue(value + 1)
        self.progress_bar.update()

    def set_text(self, text):
        self.progress_bar.setFormat(text)
        self.progress_bar.update()

    def reset_bar(self):
        self.progress_bar.reset()
        self.progress_bar.update()

