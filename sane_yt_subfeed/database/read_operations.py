from timeit import default_timer

from sqlalchemy import desc

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.write_operations import UpdateVideosThread
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.youtube.thumbnail_handler import thumbnails_dl_and_paths, download_thumbnails_threaded
from sane_yt_subfeed.youtube.update_videos import refresh_uploads


def get_newest_stored_videos(limit, filter_downloaded=False):
    """

    :param limit:
    :param filter_downloaded:
    :return: list(VideoD)
    """
    if filter_downloaded:
        db_videos = db_session.query(Video).order_by(desc(Video.date_published)).filter(Video.downloaded != '1').limit(
            limit).all()
    else:
        db_videos = db_session.query(Video).order_by(desc(Video.date_published)).limit(limit).all()
    db_session.remove()
    return Video.to_video_ds(db_videos)


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


def refresh_and_get_newest_videos(limit, filter_downloaded=False):
    videos = refresh_uploads()
    UpdateVideosThread(videos).start()
    if filter_downloaded:
        return_list = compare_db_filtered(videos, limit, True, True)
    else:
        return_list = videos[:limit]
    return_list = download_thumbnails_threaded(return_list)
    UpdateVideosThread(return_list)
    return return_list
