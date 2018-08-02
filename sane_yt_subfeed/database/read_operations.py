import datetime
import time

from sqlalchemy import desc

from sane_yt_subfeed.config_handler import read_config
from sane_yt_subfeed.controller.listeners import LISTENER_SIGNAL_NORMAL_REFRESH, LISTENER_SIGNAL_DEEP_REFRESH
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.engine_statements import get_video_by_id_stmt
from sane_yt_subfeed.database.orm import db_session, engine
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.controller.dir_handler import get_yt_file
from sane_yt_subfeed.youtube.thumbnail_handler import download_thumbnails_threaded
from sane_yt_subfeed.youtube.update_videos import refresh_uploads
from sqlalchemy.sql.expression import false, true, or_


def get_newest_stored_videos(limit, filter_downloaded=False):
    """

    :param limit:
    :param filter_downloaded:
    :return: list(VideoD)
    """
    if filter_downloaded:
        db_videos = db_session.query(Video).order_by(desc(Video.date_published)).filter(
            Video.downloaded != '1', Video.discarded != '1').limit(
            limit).all()
    else:
        db_videos = db_session.query(Video).order_by(desc(Video.date_published)).limit(limit).all()
    videos = Video.to_video_ds(db_videos)
    db_session.remove()
    return videos


def get_best_downloaded_videos(limit, filter_watched=True):
    """

    :param filter_watched:
    :param limit:
    :return: list(VideoD)
    """
    if filter_watched:
        db_videos = db_session.query(Video).order_by(desc(Video.date_published)).filter(
                Video.vid_path != "", or_(Video.watched.is_(None), Video.watched == false())).limit(limit).all()
    else:
        db_videos = db_session.query(Video).order_by(desc(Video.date_published)).filter(
                Video.vid_path != "").limit(limit).all()
    videos = Video.to_video_ds(db_videos)
    db_session.remove()
    if len(videos) < limit:
        for _ in range(limit-len(videos)):
            videos.append(VideoD(None))
    return videos


def compare_db_filtered(videos, limit, discarded=False, downloaded=False):
    return_list = []
    counter = 0
    for video in videos:
        db_vid = db_session.query(Video).get(video.video_id)
        if db_vid:
            if db_vid.downloaded and downloaded:
                continue
            elif db_vid.discarded and discarded:
                continue
            else:
                return_list.append(db_vid.to_video_d(video))
                counter += 1
        else:
            return_list.append(video)
            counter += 1
        if counter >= limit:
            break
    db_session.remove()
    return return_list


def check_for_new(videos, deep_refresh=False):
    # FIXME: add to progress bar
    # start_time = timeit.default_timer()
    for vid in videos:
        stmt = get_video_by_id_stmt(vid)
        db_video = engine.execute(stmt).first()
        if not db_video:
            # FIXME: uses wrong timezones
            vid_age = datetime.datetime.utcnow() - vid.date_published
            if deep_refresh:
                if vid_age > datetime.timedelta(hours=1):
                    vid.missed = True
                else:
                    vid.new = True
            else:
                if vid_age > datetime.timedelta(hours=12):
                    vid.missed = True
                else:
                    vid.new = True
        else:
            pass
    # print(timeit.default_timer() - start_time)
    return videos


def refresh_and_get_newest_videos(limit, filter_downloaded=False, progress_listener=None,
                                  refresh_type=LISTENER_SIGNAL_NORMAL_REFRESH):
    if progress_listener:
        progress_listener.progress_bar.setVisible(True)
        progress_listener.resetBar.emit()
    videos = refresh_uploads(progress_bar_listener=progress_listener, add_to_max=2 * limit, refresh_type=refresh_type)
    if filter_downloaded:
        return_list = compare_db_filtered(videos, limit, True, True)
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
