import sys

import click

from sane_yt_subfeed.main import run_with_gui, run_print, run_channels_test


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
            # Print the error and traceback
            print(exctype, value, traceback)
            # Call the normal Exception hook after
            sys._excepthook(exctype, value, traceback)
            sys.exit(1)

        # Set the exception hook to our wrapping function
        sys.excepthook = my_exception_hook

        run_with_gui()


if __name__ == '__main__':
    cli()
