from sqlalchemy import desc

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.youtube.thumbnail_handler import thumbnails_dl_and_paths
from sane_yt_subfeed.youtube.update_videos import refresh_uploads


def get_newest_stored_videos(limit, filter_downloaded=False):
    if filter_downloaded:
        return db_session.query(Video).order_by(desc(Video.date_published)).filter(Video.downloaded != '1').limit(
            limit).all()
    else:
        return db_session.query(Video).order_by(desc(Video.date_published)).limit(limit).all()


def refresh_and_get_newest_videos(limit, filter_downloaded=False):
    refresh_uploads()
    if filter_downloaded:
        vid_list = db_session.query(Video).order_by(desc(Video.date_published)).filter(Video.downloaded != '1').limit(
            limit).all()
        thumbnails_dl_and_paths(vid_list)
    else:
        vid_list = db_session.query(Video).order_by(desc(Video.date_published)).limit(limit).all()
        thumbnails_dl_and_paths(vid_list)
    return vid_list
