import datetime
import threading
from sqlalchemy import desc, asc

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners.database.database_listener import DatabaseListener
from sane_yt_subfeed.controller.static_controller_vars import LISTENER_SIGNAL_NORMAL_REFRESH, \
    LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.database.engine_statements import get_video_by_vidd_stmt, get_video_by_id_stmt
from sane_yt_subfeed.database.orm import db_session, engine
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.write_operations import UpdateVideosThread, UpdateVideosExtraInfoThreaded
from sane_yt_subfeed.exceptions.sane_aborted_operation import SaneAbortedOperation
from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded
from sane_yt_subfeed.youtube.update_videos import refresh_uploads, get_extra_videos_information

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)


def get_newest_stored_videos(limit, filters=(~Video.downloaded, ~Video.discarded)):
    """

    :param filters:
    :param limit:
    :return: list(VideoD)
    """
    logger.info("Getting newest stored videos (filters={})".format(filters))

    filter_days = read_config('Requests', 'filter_videos_days_old')
    if filter_days >= 0:
        date = datetime.datetime.utcnow() - datetime.timedelta(days=filter_days)
        filters = filters + (Video.date_published > date,)

    DatabaseListener.static_instance.startRead.emit(threading.get_ident())
    db_videos = db_session.query(Video).order_by(desc(Video.date_published)).filter(*filters).limit(limit).all()
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())
    videos = Video.to_video_ds(db_videos)
    db_session.remove()
    return videos


def get_best_playview_videos(limit,
                             filters=(~Video.watched, Video.downloaded, ~Video.discarded), sort_method=(
                asc(Video.watch_prio), desc(Video.date_downloaded), desc(Video.date_published))):
    """

    :param filters: Tuple of filters
    :param sort_method:
    :param limit:
    :return: list(VideoD)
    """
    db_query = db_session.query(Video)

    db_query = db_query.filter(*filters)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())
    db_videos = db_query.order_by(*sort_method).limit(limit).all()
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())
    videos = Video.to_video_ds(db_videos)
    db_session.remove()
    return videos


def compare_db_filtered(videos, limit, discarded=False, downloaded=False):
    logger.info("Comparing filtered videos with DB")
    return_list = []
    counter = 0

    filter_days = read_config('Requests', 'filter_videos_days_old')

    DatabaseListener.static_instance.startRead.emit(threading.get_ident())
    for video in videos:
        if filter_days >= 0:
            date = datetime.datetime.utcnow() - datetime.timedelta(days=filter_days)
            if video.date_published < date:
                break
        db_vid = get_vid_by_id(video.video_id)
        if db_vid:
            if db_vid.downloaded:
                if downloaded:
                    continue
            if db_vid.discarded:
                if discarded:
                    continue
            return_list.append(Video.to_video_d(video))
            counter += 1
        else:
            return_list.append(video)
            counter += 1
        if counter >= limit:
            break
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())
    db_session.remove()
    return return_list


def check_for_new(videos, deep_refresh=False):
    logger.info("Checking for new videos{}".format((" (deep refresh)" if deep_refresh else "")))
    # FIXME: add to progress bar
    # start_time = timeit.default_timer()
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())
    for vid in videos:
        stmt = get_video_by_vidd_stmt(vid)
        db_video = engine.execute(stmt).first()
        if not db_video:
            vid_age = datetime.datetime.utcnow() - vid.date_published
            if deep_refresh:
                if vid_age > datetime.timedelta(hours=1):
                    vid.missed = True
                    logger.info("Missed video: {}".format(vid))
                else:
                    vid.new = True
                    logger.info("New video: {}".format(vid))
            else:
                if vid_age > datetime.timedelta(hours=12):
                    vid.missed = True
                    logger.info("Missed video: {}".format(vid))
                else:
                    vid.new = True
                    logger.info("New video: {}".format(vid))
        else:
            pass
    # print(timeit.default_timer() - start_time)
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())
    return videos


def refresh_and_get_newest_videos(limit, filter_downloaded=True, filter_discarded=True, progress_listener=None,
                                  refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
    """
    Refresh subscription feed and get newest videos from local DB
    :param limit:
    :param filter_downloaded:
    :param filter_discarded:
    :param progress_listener:
    :param refresh_type:
    :return:
    """
    logger.info("Refreshing and getting newest videos")
    if progress_listener:
        progress_listener.progress_bar.setVisible(True)
        progress_listener.resetBar.emit()

    try:
        videos = refresh_uploads(progress_bar_listener=progress_listener, add_to_max=2 * limit,
                                 refresh_type=refresh_type)
    except SaneAbortedOperation as exc_sao:
        # Clean up progress bar after aborted operation
        if progress_listener:
            progress_listener.progress_bar.setVisible(False)
            progress_listener.resetBar.emit()
            raise exc_sao
    except Exception as exc_other:
        logger.critical("Unexpected exception occurred in refresh_and_get_newest_videos!", exc_info=exc_other)
        pass

    if filter_downloaded or filter_discarded:
        return_list = compare_db_filtered(videos, limit, discarded=filter_discarded, downloaded=filter_downloaded)
    else:
        return_list = videos[:limit]

    if refresh_type == LISTENER_SIGNAL_DEEP_REFRESH:
        return_list = check_for_new(return_list, deep_refresh=True)
    else:
        return_list = check_for_new(return_list)

    UpdateVideosThread(videos).start()
    if len(return_list) > 0:
        download_thumbnails_threaded(return_list, progress_listener=progress_listener)
        return_list = get_extra_videos_information(return_list)
        UpdateVideosExtraInfoThreaded(return_list).start()
    else:
        logger.info("Skipping thumbnails download and db update as return list is empty")

    if progress_listener:
        progress_listener.progress_bar.setVisible(False)
        progress_listener.resetBar.emit()
    return return_list


def get_vid_by_id(video_id):
    stmt = get_video_by_id_stmt(video_id)
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())
    db_video = engine.execute(stmt).first()
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())
    return db_video


def get_videos_by_ids(video_ids):
    DatabaseListener.static_instance.startRead.emit(threading.get_ident())
    db_videos = engine.execute(Video.__table__.select(Video.video_id.in_(video_ids)))
    DatabaseListener.static_instance.finishRead.emit(threading.get_ident())
    return_videos = Video.to_video_ds(db_videos)
    return return_videos
