import datetime
import sys

import click
from sqlalchemy import or_
from subprocess import check_output

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.database.video import Video

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.main import run_with_gui, run_print, run_channels_test
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions

exceptions = []
exc_id = 0


@click.option(u'--no_gui', is_flag=True)
@click.option(u'--test-channels', is_flag=True)
@click.option(u'--update-watch-prio', is_flag=True)
@click.option(u'--set-watched-day')
@click.option(u'--print_subscriptions', is_flag=True)
@click.command()
def cli(no_gui, test_channels, update_watch_prio, set_watched_day, print_subscriptions):
    logger = create_logger(__name__)
    if no_gui:
        run_print()
    if update_watch_prio:
        videos = db_session.query(Video).all()
        watch_prio = read_config('Play', 'default_watch_prio')
        logger.debug("Setting watch_prio {}, for: {} videos".format(watch_prio, len(videos)))
        for video in videos:
            video.watch_prio = watch_prio
        db_session.commit()
        return

    if set_watched_day:
        videos = db_session.query(Video).filter(or_(Video.downloaded == True, (Video.vid_path.is_(None)))).all()
        for video in videos:
            vid_age = datetime.datetime.utcnow() - video.date_published
            if vid_age > datetime.timedelta(days=int(set_watched_day)):
                logger.debug("Setting watched, {} - {} - {}".format(vid_age, video.title, video.__dict__))
                video.watched = True
        db_session.commit()
        return
    if test_channels:
        run_channels_test()
    if print_subscriptions:
        cached_subs = True
        subs = get_subscriptions(cached_subs)
        for channel in subs:
            if channel.subscribed_override:
                print(("[{}]    {} [Subscription override]".format(channel.id, channel.title)))
            else:
                print(("[{}]    {}".format(channel.id, channel.title)))
    else:
        """
        PyQT raises and catches exceptions, but doesn't pass them along. 
        Instead it just exits with a status of 1 to show an exception was caught. 
        """
        # Back up the reference to the exceptionhook
        sys._excepthook = sys.excepthook

        def my_exception_hook(exctype, value, traceback):
            global exc_id, exceptions
            # Ignore KeyboardInterrupt so a console python program can exit with Ctrl + C.
            if issubclass(exctype, KeyboardInterrupt):
                sys.__excepthook__(exctype, value, traceback)
                return

            # Log the exception with the logger
            logger.exception("Intercepted Exception #{}".format(exc_id), exc_info=(exctype, value, traceback))

            # Store intercepted exceptions in a reference list of lists
            exceptions.append([exctype, value, traceback, exc_id])

            # Increment Exception Identifier
            exc_id += 1

            # Call the normal Exception hook after
            sys._excepthook(exctype, value, traceback)

            # sys.exit(1)       # Alternatively, exit

        # Set the exception hook to our wrapping function
        sys.excepthook = my_exception_hook

        # Log the current ulimit
        if sys.platform.startswith('linux'):
            ulimit_data = check_output("ulimit -a", shell=True)
            logger.info("=== ulimit info on next line ===")
            logger.info(ulimit_data.decode('utf8'))

        run_with_gui(exceptions)


if __name__ == '__main__':
    cli()
