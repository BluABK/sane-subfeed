import datetime
import threading
from sqlalchemy import desc, asc

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.controller.listeners.database.database_listener import DatabaseListener
from sane_yt_subfeed.controller.static_controller_vars import LISTENER_SIGNAL_NORMAL_REFRESH, \
    LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.database.engine_statements import get_video_by_vidd_stmt, get_video_by_id_stmt
from sane_yt_subfeed.database.orm import db_session, engine
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideosThread, UpdateVideosExtraInfoThreaded
from sane_yt_subfeed.exceptions.sane_aborted_operation import SaneAbortedOperation
from sane_yt_subfeed.handlers.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded
from sane_yt_subfeed.youtube.update_videos import refresh_uploads, get_extra_videos_information

logger = create_logger(__name__)


def get_db_videos_subfeed(limit, filters=(~Video.downloaded, ~Video.discarded)):
    """
    Get a list of videos from the database, limited by limit and filters.

    :param filters: Tuple of SQLAlchemy Column(Boolean) objects.
    :param limit:   Integer value determining how many videos to grab.
    :return:        A list of VideoD objects.
    """
    logger.info("Getting newest stored videos (filters={})".format(filters))

    # Check whether "filter by video age" is enabled, if so apply the filter to filters.
    filter_days = read_config('Requests', 'filter_videos_days_old')
    if filter_days >= 0:
        date = datetime.datetime.utcnow() - datetime.timedelta(days=filter_days)
        filters = filters + (Video.date_published > date,)

    # Signal DB listener about started read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())

    # Execute query, ordered by publish date (descending), filtered by filters and limited by limit.
    db_videos = db_session.query(Video).order_by(desc(Video.date_published)).filter(*filters).limit(limit).all()

    # Signal DB listener about finished read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())

    # Convert Video objects to VideoD (Detached model) objects.
    videos = Video.to_video_ds(db_videos)

    # Close DB Query session.
    db_session.remove()

    return videos


def get_db_videos_playback(limit,
                           filters=(~Video.watched, Video.downloaded, ~Video.discarded), sort_method=(
                                    asc(Video.watch_prio), desc(Video.date_downloaded), desc(Video.date_published))):
    """
    Get a list of videos from the database, limited by limit and filters. Sorted by sort_method.

    :param filters:     Tuple of SQLAlchemy Column(Boolean) objects.
    :param sort_method: Tuple of SQLAlchemy sort expressions.
    :param limit:       Integer value determining how many videos to grab.
    :return:            A list of VideoD objects.
    """
    # Initiate DB Query session.
    db_query = db_session.query(Video)

    # Apply filters to query.
    db_query = db_query.filter(*filters)

    # Signal DB listener about started read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())

    # Execute query, ordered by sort_method and limited by limit.
    db_videos = db_query.order_by(*sort_method).limit(limit).all()

    # Signal DB listener about finished read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())

    # Convert Video objects to VideoD (Detached model) objects.
    videos = Video.to_video_ds(db_videos)

    # Close DB Query session.
    db_session.remove()

    return videos


def filter_videos(videos, limit, filter_discarded=False, filter_downloaded=False):
    """
    Takes a list of videos and excludes items that match any enabled exclusion filter.

    :param videos:              A list of Video objects to be compared.
    :param limit:               Integer value determining how many videos to return.
    :param filter_discarded:    Boolean determining whether or not to exclude discarded videos.
    :param filter_downloaded:   Boolean determining whether or not to exclude filter_downloaded videos.
    :return:                    A list of VideoD objects.
    """
    logger.info("Comparing filtered videos with DB")
    return_list = []
    counter = 0

    # Check whether "filter by video age" is enabled, if so apply the filter to filters.
    filter_days = read_config('Requests', 'filter_videos_days_old')

    # Signal DB listener about started read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())

    # Iterate through videos:
    for video in videos:
        # If "filter by video age" is enabled, skip videos older than filter_days days.
        if filter_days >= 0:
            date = datetime.datetime.utcnow() - datetime.timedelta(days=filter_days)
            if video.date_published < date:
                break

        # Check if video is in database, if so, convert it and add it to list, unless it matches an exclusion filter.
        db_vid = get_vid_by_id(video.video_id)

        if db_vid:
            # Skip video if it matches an enabled exclusion filter.
            if (db_vid.downloaded and filter_downloaded) or (db_vid.discarded and filter_discarded):
                continue

            # Convert Video object to VideoD (Detached model) object and append it to the list, then increment counter.
            return_list.append(Video.to_video_d(video))
            counter += 1

        # If video isn't in database, no filters apply and it can simply be appended to the list.
        else:
            # Append VideoD object to list, then increment counter.
            return_list.append(video)
            counter += 1

        # Break once the limit has been reached.
        if counter >= limit:
            break

    # Signal DB listener about finished read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())

    # Close DB Query session.
    db_session.remove()

    return return_list


def check_for_new(videos, refresh_type):
    """
    Check for new video uploads.
    :param videos:
    :param refresh_type:
    :return:
    """
    logger.info("Checking for new videos{}".format((" (deep refresh)"
                                                    if refresh_type == LISTENER_SIGNAL_DEEP_REFRESH else "")))
    # FIXME: add to progress bar
    # Signal DB listener about started read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())

    # Iterate through videos.
    for vid in videos:
        # Get the Video id using an engine statement and check if the video is in the database.
        stmt = get_video_by_vidd_stmt(vid)
        db_video = engine.execute(stmt).first()

        # If video is not in database, apply new/missing conditions to it.
        if not db_video:
            # Determine the
            vid_age = datetime.datetime.utcnow() - vid.date_published
            # FIXME: Make missed video age condition user configurable.
            if vid_age > datetime.timedelta(hours=12):
                vid.missed = True
                logger.info("Missed video: {}".format(vid))
            else:
                vid.new = True
                logger.info("New video: {}".format(vid))
        # If video is in database, do nothing.
        else:
            pass

    # Signal DB listener about finished read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())

    return videos


def refresh_and_get_newest_videos(limit, filter_downloaded=True, filter_discarded=True, progress_listener=None,
                                  refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
    """
    Refresh subscription feed and get newest videos from Database.

    :param limit:               Integer value determining how many videos to return.
    :param filter_discarded:    Boolean determining whether or not to exclude discarded videos.
    :param filter_downloaded:   Boolean determining whether or not to exclude filter_downloaded videos.
    :param progress_listener:   QProgressBar listener.
    :param refresh_type:        Listener signal determining whether to do a normal or deep refresh.
    :return:
    """
    logger.info("Refreshing and getting newest videos")

    # Spawn a QProgressBar, if listener is given.
    if progress_listener:
        progress_listener.progress_bar.setVisible(True)
        progress_listener.resetBar.emit()

    try:
        # Get a list of videos by refreshing the subscription feed.
        videos = refresh_uploads(progress_bar_listener=progress_listener, add_to_max=2 * limit,
                                 refresh_type=refresh_type)

        # If filters are enabled, run the videos through a filter function.
        if filter_downloaded or filter_discarded:
            return_list = filter_videos(videos, limit, filter_discarded=filter_discarded,
                                        filter_downloaded=filter_downloaded)

        # If no filters are enabled, simply add limit amount of videos to the list.
        else:
            return_list = videos[:limit]

        # Check for new videos (modify list directly).
        return_list = check_for_new(return_list, refresh_type)

        # Update videos (threaded).
        UpdateVideosThread(videos).start()
        # Check that video list isn't empty.
        if len(return_list) > 0:
            # Download video thumbnails (threaded).
            download_thumbnails_threaded(return_list, progress_listener=progress_listener)

            # Get additional video information (threaded) that isn't included in the standard grab function.
            return_list = get_extra_videos_information(return_list)
            UpdateVideosExtraInfoThreaded(return_list).start()
        else:
            logger.info("Skipping thumbnails download and db update as return list is empty")

        if progress_listener:
            progress_listener.progress_bar.setVisible(False)
            progress_listener.resetBar.emit()

        return return_list

    except SaneAbortedOperation as exc_sao:
        # Clean up progress bar after aborted operation
        if progress_listener:
            progress_listener.progress_bar.setVisible(False)
            progress_listener.resetBar.emit()

            raise exc_sao
    except Exception as exc_other:
        logger.critical("Unexpected exception occurred in refresh_and_get_newest_videos!", exc_info=exc_other)

        raise exc_other


def get_vid_by_id(video_id):
    """
    Get video by id using a __table__ SELECT WHERE engine statement.
    :param video_id: Video ID string
    :return:
    """
    # Create a __table__ SELECT WHERE video_id=this_video_id engine statement.
    stmt = get_video_by_id_stmt(video_id)

    # Signal DB listener about started read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())

    # Execute engine statement, and only return the first result.
    db_video = engine.execute(stmt).first()

    # Signal DB listener about finished read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())

    return db_video


def get_videos_by_ids(video_ids):
    """
    Get videos by IDs using a __table__ SELECT WHERE engine statement.
    :param video_ids: Video ID strings
    :return:
    """
    # Signal DB listener about started read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())

    # Execute SELECT engine statement for each video.
    db_videos = engine.execute(Video.__table__.select(Video.video_id.in_(video_ids)))

    # Signal DB listener about finished read operation (Used in DB status indicator and logs)
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())

    # Convert Video objects to VideoD (Detached model) objects.
    videos = Video.to_video_ds(db_videos)

    return videos
