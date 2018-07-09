from timeit import default_timer

from sqlalchemy import desc

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.threaded_db_operations import UpdateVideosThreadSnippets
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.youtube.thumbnail_handler import thumbnails_dl_and_paths
from sane_yt_subfeed.youtube.update_videos import refresh_uploads


def get_newest_stored_videos(limit, filter_downloaded=False):
    if filter_downloaded:
        return db_session.query(Video).order_by(desc(Video.date_published)).filter(Video.downloaded != '1').limit(
            limit).all()
    else:
        return db_session.query(Video).order_by(desc(Video.date_published)).limit(limit).all()


def compare_db_filtered(videos, limit):
    return_list = []
    counter = 0
    for video in videos:
        db_vid = db_session.query(Video).get(video.video_id)
        if db_vid:
            if db_vid.downloaded:
                continue
            else:
                return_list.append(db_vid)
                counter += 1
        else:
            return_list.append(video)
            counter += 1
        if counter >= limit:
            break
    return return_list


def refresh_and_get_newest_videos(limit, filter_downloaded=False):
    return_list = refresh_uploads()
    if filter_downloaded:
        return_list = compare_db_filtered(return_list, limit)
    thumbnails_dl_and_paths(return_list)
    db_thread = UpdateVideosThreadSnippets(return_list)
    db_thread.start()
    return return_list
