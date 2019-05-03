import sys

import copy
from PyQt5.QtCore import QObject, pyqtSignal

from sane_yt_subfeed import create_logger


class SaneExceptionHandler(QObject):
    """
    PyQT raises and catches exceptions, but doesn't pass them along.
    Instead it just exits with a status of 1 to show an exception was caught.

    This exception handler overrides the sys._excepthook in order to handle exceptions sanely.

    Basic setup/usage example for a QApplication:
    # Create the Exception Handler
    exceptionHandler = SaneExceptionHandler()
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook
    # Set the exception hook to be wrapped by the Exception Handler
    sys.excepthook = exceptionHandler.handler
    """
    exc_id = 0
    exceptions = []
    errorSignal = pyqtSignal()
    silentSignal = pyqtSignal()

    def __init__(self, app_ref=None, use_list=True, display=True):
        super(SaneExceptionHandler, self).__init__()
        self.app_ref = app_ref
        self.use_list = use_list
        self.logger = create_logger(__name__)

        # Back up the reference to the exception hook
        sys._excepthook = sys.excepthook
        # noinspection PyProtectedMember
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

        # Increment the exception identifier
        self.exc_id += 1

        # Call the original Exception hook
        self.original_excepthook(exctype, value, traceback)

        # Finally call an exception hook
        if self.app_ref is None:
            # Call the original Exception hook
            # self.original_excepthook(exctype, value, traceback)
            return
        else:
            if self.use_list:
                # Add exception to a list to be handled later
                self.add_exception(exctype, value, traceback)

        # Call custom raise_exception function in QApplication parent
        try:
            self.app_ref.raise_exception(exctype, value, traceback)
        except AttributeError as ae_exc:
            self.logger.error("Exception IGNORED: Please implement raise_exception function in your app_ref")
            pass

    def add_exception(self, exctype, value, traceback):
        """
        Adds a list of the constructors of an Exception to the exceptions list.
        :param exctype:
        :param value:
        :param traceback:
        :return:
        """
        self.exceptions.append([exctype, value, traceback])

    def clear_exceptions(self):
        """
        Clears the exceptions list.
        :return:
        """
        self.exceptions.clear()

    def pop_exception(self):
        """
        Pops the last exception in the exceptions list.
        :return:
        """
        try:
            return self.exceptions.pop()
        except IndexError:
            pass

    def pop_exceptions(self):
        """
        Pops the entire exceptions list.
        :return:
        """
        try:
            popped_exceptions = copy.copy(self.exceptions)
            self.clear_exceptions()
            return popped_exceptions
        except IndexError:
            pass
