import sys
from PyQt5.QtCore import QObject, pyqtSignal

from sane_yt_subfeed import create_logger


class SaneExceptionHandler(QObject):
    """
    PyQT raises and catches exceptions, but doesn't pass them along.
    Instead it just exits with a status of 1 to show an exception was caught.

    This exception handler overrides the sys._excepthook in order to handle exceptions sanely.
    """
    exc_id = 0
    errorSignal = pyqtSignal()
    silentSignal = pyqtSignal()

    def __init__(self):
        super(SaneExceptionHandler, self).__init__()
        self.logger = create_logger(__name__)
        # Back up the reference to the exception hook
        sys._excepthook = sys.excepthook
        self.original_excepthook = sys._excepthook

    def handler(self, exctype, value, traceback):
        # Ignore KeyboardInterrupt so a console python program can exit with Ctrl + C.
        if issubclass(exctype, KeyboardInterrupt):
            sys.__excepthook__(exctype, value, traceback)
            return

        # Emit error signal
        self.errorSignal.emit()

        # Log the exception with the logger
        self.logger.exception("Intercepted Exception #{}".format(self.exc_id), exc_info=(exctype, value, traceback))

        # Increment Exception Identifier
        self.exc_id += 1

        # Finally call the original Exception hook
        self.original_excepthook(exctype, value, traceback)


"""
Basic setup/usage in a QApplication:

# Create the Exception Handler
exceptionHandler = SaneExceptionHandler()
# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook
# Set the exception hook to be wrapped by the Exception Handler
sys.excepthook = exceptionHandler.handler
"""
