from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.video import Video


def filter_downloaded(vid_list, nr):
    return_list = []
    for vid in vid_list:
        # TODO do not need this vid query, if they are connected to db
        db_vid = db_session.query(Video).get(vid.video_id)
        if not db_vid.downloaded:
            return_list.append(vid)
        if len(return_list) >= nr:
            return return_list
    raise IndexError

