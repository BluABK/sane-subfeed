import datetime
import time

from sqlalchemy import desc, asc

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.static_controller_vars import LISTENER_SIGNAL_NORMAL_REFRESH, \
    LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.database.database_static_vars import ORDER_METHOD_DATE_DOWNLOADED_UPLOAD_DATE, \
    ORDER_METHOD_PRIO_DATE_DOWNLOADED_UPLOAD_DATE
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.engine_statements import get_video_by_vidd_stmt, get_video_by_id_stmt
from sane_yt_subfeed.database.orm import db_session, engine
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded
from sane_yt_subfeed.youtube.update_videos import refresh_uploads
from sane_yt_subfeed.log_handler import create_logger
from sqlalchemy.sql.expression import false, true, or_

# FIXME: module level logger not suggested: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = create_logger(__name__)


def get_newest_stored_videos(limit, filter_downloaded=False):
    """

    :param limit:
    :param filter_downloaded:
    :return: list(VideoD)
    """
    filters = ()

    filter_days = read_config('Requests', 'filter_videos_days_old')
    if filter_days >= 0:
        date = datetime.datetime.utcnow() - datetime.timedelta(days=filter_days)
        filters = filters + (Video.date_published > date,)

    if filter_downloaded:
        filters = filters + (Video.downloaded != '1', Video.discarded != '1')

    logger.info("Getting newest stored videos (filters={})".format(filters))
    db_videos = db_session.query(Video).order_by(desc(Video.date_published)).filter(*filters
            ).limit(
            limit).all()
    videos = Video.to_video_ds(db_videos)
    db_session.remove()
    return videos


def get_best_downloaded_videos(limit,
                               filters=(or_(Video.watched == false(), or_(Video.watched.is_(None))),),
                               sort_method=(
                                       asc(Video.watch_prio), desc(Video.date_downloaded), desc(Video.date_published))):
    """

    :param filters: Tuple of filters
    :param sort_method:
    :param limit:
    :return: list(VideoD)
    """
    db_query = db_session.query(Video)

    # FIXME: move out of this function
    if read_config('Play', 'use_url_as_path'):
        filters = filters + (Video.downloaded == True,)
    else:
        filters = filters + (Video.vid_path.isnot(None),)

    db_query = db_query.filter(*filters)
    db_videos = db_query.order_by(*sort_method).limit(limit).all()
    videos = Video.to_video_ds(db_videos)
    db_session.remove()
    return videos


def compare_db_filtered(videos, limit, filters=(Video.discarded == False, Video.downloaded == False),
                        sort_method=(desc(Video.date_published),)):
    logger.info("Comparing filtered videos with DB")

    # FIXME: move out of here
    filter_days = read_config('Requests', 'filter_videos_days_old')
    if filter_days >= 0:
        date = datetime.datetime.utcnow() - datetime.timedelta(days=filter_days)
        filters = filters + (Video.date_published > date,)
    return_list = []
    # counter = 0
    video_ids = [video.video_id for video in videos]
    for i in range(0, len(video_ids), limit * 2):
        temp_keys_list = video_ids[i:i + limit * 2]
        return_list.extend(
            db_session.query(Video).filter(Video.video_id.in_(temp_keys_list), *filters).order_by(*sort_method).limit(
                limit - len(return_list)).all())
    return_list = Video.to_video_ds(return_list)
    db_session.remove()
    return return_list


def check_for_new(videos, deep_refresh=False):
    logger.info("Checking for new videos{}".format((" (deep refresh)" if deep_refresh else "")))
    # FIXME: add to progress bar
    # start_time = timeit.default_timer()
    for vid in videos:
        stmt = get_video_by_vidd_stmt(vid)
        db_video = engine.execute(stmt).first()
        if not db_video:
            vid_age = datetime.datetime.utcnow() - vid.date_published
            if deep_refresh:
                if vid_age > datetime.timedelta(hours=1):
                    vid.missed = True
                    logger.info("Missed video: {} - {} [{}]".format(vid.channel_title, vid.title, vid.url_video))
                else:
                    vid.new = True
                    logger.info("New video: {} - {} [{}]".format(vid.channel_title, vid.title, vid.url_video))
            else:
                if vid_age > datetime.timedelta(hours=12):
                    vid.missed = True
                    logger.info("Missed video: {} - {} [{}]".format(vid.channel_title, vid.title, vid.url_video))
                else:
                    vid.new = True
                    logger.info("New video: {} - {} [{}]".format(vid.channel_title, vid.title, vid.url_video))
        else:
            pass
    # print(timeit.default_timer() - start_time)
    return videos


def refresh_and_get_newest_videos(limit, filter_downloaded=False, progress_listener=None,
                                  refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
    logger.info("Refreshing and getting newest videos")
    if progress_listener:
        progress_listener.progress_bar.setVisible(True)
        progress_listener.resetBar.emit()
    videos = refresh_uploads(progress_bar_listener=progress_listener, add_to_max=2 * limit, refresh_type=refresh_type)
    if filter_downloaded:
        return_list = compare_db_filtered(videos, limit)
    else:
        return_list = videos[:limit]

    if refresh_type == LISTENER_SIGNAL_DEEP_REFRESH:
        return_list = check_for_new(return_list, deep_refresh=True)
    else:
        return_list = check_for_new(return_list)

    UpdateVideosThread(videos).start()
    download_thumbnails_threaded(return_list, progress_listener=progress_listener)
    UpdateVideosThread(return_list, update_existing=True).start()
    if progress_listener:
        progress_listener.progress_bar.setVisible(False)
        progress_listener.resetBar.emit()
    return return_list


def get_vid_by_id(video_id):
    stmt = get_video_by_id_stmt(video_id)
    db_video = engine.execute(stmt).first()
    return db_video


def get_videos_by_ids(video_ids):
    db_videos = engine.execute(Video.__table__.select(Video.video_id.in_(video_ids)))
    return_videos = Video.to_video_ds(db_videos)
    return return_videos
