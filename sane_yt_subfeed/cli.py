import sys

import click

from sane_yt_subfeed.main import run_with_gui, run_print, run_channels_test
from sane_yt_subfeed.log_handler import logger


@click.option(u'--no_gui', is_flag=True)
@click.option(u'--test_channels', is_flag=True)
@click.command()
def cli(no_gui, test_channels):
    if no_gui:
        run_print()
    if test_channels:
        run_channels_test()
    else:
        """
        PyQT raises and catches exceptions, but doesn't pass them along. 
        Instead it just exits with a status of 1 to show an exception was caught. 
        """
        # Back up the reference to the exceptionhook
        sys._excepthook = sys.excepthook

        def my_exception_hook(exctype, value, traceback):
            # Ignore KeyboardInterrupt so a console python program can exit with Ctrl + C.
            if issubclass(exctype, KeyboardInterrupt):
                sys.__excepthook__(exctype, value, traceback)
                return

            # Log the exception with the logger
            logger.critical("Uncaught Exception (likely Qt)", exc_info=(exctype, value, traceback))

            # Call the normal Exception hook after
            sys._excepthook(exctype, value, traceback)

            # sys.exit(1)       # Alternatively, exit

        # Set the exception hook to our wrapping function
        sys.excepthook = my_exception_hook

        run_with_gui()


if __name__ == '__main__':  # FIXME: Dead code, since __main__.py?
    cli()
