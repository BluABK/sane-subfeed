import datetime
import sys

import click

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.video import Video

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.main import run_with_gui, run_print, run_channels_test
from sane_yt_subfeed.log_handler import logger


@click.option(u'--no_gui', is_flag=True)
@click.option(u'--test-channels', is_flag=True)
@click.option(u'--update-watch-prio', is_flag=True)
@click.option(u'--set-watched-day')
@click.command()
def cli(no_gui, test_channels, update_watch_prio, set_watched_day):
    if no_gui:
        run_print()
    if update_watch_prio:
        videos = db_session.query(Video).all()
        watch_prio = read_config('Play', 'default_watch_prio')
        for video in videos:
            video.watch_prio = watch_prio
        db_session.commit()
        return

    if set_watched_day:
        videos = db_session.query(Video).filter(Video.downloaded == True).all()
        for video in videos:
            vid_age = datetime.datetime.utcnow() - video.date_published
            if vid_age > datetime.timedelta(days=int(set_watched_day)):
                video.watched = True
        db_session.commit()
        return
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
            logger.critical("Intercepted Exception", exc_info=(exctype, value, traceback))

            # Call the normal Exception hook after
            sys._excepthook(exctype, value, traceback)

            # sys.exit(1)       # Alternatively, exit

        # Set the exception hook to our wrapping function
        sys.excepthook = my_exception_hook

        run_with_gui()


if __name__ == '__main__':  # FIXME: Dead code, since __main__.py?
    cli()
