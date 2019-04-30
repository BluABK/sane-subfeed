import sys

import click
import datetime
from sqlalchemy import or_, and_

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.main import run_with_gui, run_channels_test, run_with_cli, cli_refresh_and_print_subfeed
from sane_yt_subfeed.youtube.update_videos import load_keys
from sane_yt_subfeed.youtube.youtube_requests import get_subscriptions
from sane_yt_subfeed.cli import print_functions
import sane_yt_subfeed.youtube as youtube

exceptions = []
exc_id = 0
LEGACY_EXCEPTION_HANDLER = False


@click.option(u'--no_gui', is_flag=True)
@click.option(u'--test-channels', is_flag=True)
@click.option(u'--update-watch-prio', is_flag=True)
@click.option(u'--set-watched-day')
@click.option(u'--refresh_and_print_subfeed', is_flag=True)
@click.option(u'--print_subscriptions', is_flag=True)
@click.option(u'--print_downloaded_videos', is_flag=True)
@click.option(u'--print_watched_videos', is_flag=True)
@click.option(u'--print_discarded_videos', is_flag=True)
@click.option(u'--print_playlist_items', is_flag=False)
@click.option(u'--print_playlist_items_url_only', is_flag=True)
@click.command()
def cli(no_gui, test_channels, update_watch_prio, set_watched_day, refresh_and_print_subfeed, print_subscriptions,
        print_watched_videos, print_discarded_videos, print_downloaded_videos, print_playlist_items,
        print_playlist_items_url_only):
    logger = create_logger(__name__)
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
    if refresh_and_print_subfeed:
        cli_refresh_and_print_subfeed()
    if print_subscriptions:
        cached_subs = True
        subs = get_subscriptions(cached_subs)
        for channel in subs:
            if channel.subscribed_override:
                print(("[{}]    {} [Subscription override]".format(channel.id, channel.title)))
            else:
                print(("[{}]    {}".format(channel.id, channel.title)))
    if print_watched_videos:
        videos = db_session.query(Video).filter(and_(Video.watched is True, (Video.vid_path.isnot(None)))).all()
        print_functions.print_videos(videos, path_only=True)
    if print_discarded_videos:
        videos = db_session.query(Video).filter(and_(Video.discarded is True, (Video.vid_path.isnot(None)))).all()
        print_functions.print_videos(videos, path_only=True)
    if print_downloaded_videos:
        videos = db_session.query(Video).filter(and_(Video.downloaded is True, (Video.vid_path.isnot(None)))).all()
        print_functions.print_videos(videos, path_only=True)
    if print_playlist_items:
        youtube_auth_resource = load_keys(1)[0]
        playlist_video_items = []
        youtube.youtube_requests.list_uploaded_videos(youtube_auth_resource, playlist_video_items,
                                                      print_playlist_items, 50)
        for vid in playlist_video_items:
            if print_playlist_items_url_only:
                print(vid.url_video)
            else:
                print(vid)

    if no_gui:
        run_with_cli()
    else:
        if LEGACY_EXCEPTION_HANDLER:
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
                # noinspection PyProtectedMember
                sys._excepthook(exctype, value, traceback)

                # sys.exit(1)       # Alternatively, exit

            # Set the exception hook to our wrapping function
            sys.excepthook = my_exception_hook

        run_with_gui()


if __name__ == '__main__':
    cli()
