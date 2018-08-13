from sqlalchemy import text

from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.video import Video


def update_video_statement_full(db_video):
    return Video.__table__.update().where("video_id = '{}'".format(db_video.video_id)).values(
        video_id=db_video.video_id,
        channel_title=db_video.channel_title,
        title=db_video.title,
        date_published=db_video.date_published,
        description=db_video.description,
        thumbnail_path=db_video.thumbnail_path,
        playlist_pos=db_video.playlist_pos,
        url_video=db_video.url_video,
        url_playlist_video=db_video.url_playlist_video,
        thumbnails=db_video.thumbnails,
        downloaded=db_video.downloaded,
        search_item=db_video.search_item,
        discarded=db_video.discarded,
        vid_path=db_video.vid_path,
        watched=db_video.watched,
        watch_prio=db_video.watch_prio,
        date_downloaded=db_video.date_downloaded)


def update_channel_from_remote(channel):
    return Channel.__table__.update().where("id = '{}'".format(channel.id)).values(
        title=channel.title, description=channel.description, snippet=channel.snippet, playlist_id=channel.playlist_id)


def get_channel_by_id_stmt(channel):
    return Channel.__table__.select().where(text("id = '{}'".format(channel.id)))


def get_video_by_vidd_stmt(video_d):
    return Video.__table__.select().where(text("video_id = '{}'".format(video_d.video_id)))

def get_video_ids_by_video_ids_stmt(video_ids):
    return Video.__table__.select(Video.video_id.in_(video_ids))

def get_video_by_id_stmt(video_id):
    return Video.__table__.select().where(text("video_id = '{}'".format(video_id)))


# FIXME: probably outdated for variables and values
def insert_item(video):
    return {"video_id": video.video_id, "channel_title": video.channel_title,
            'title': video.title, "date_published": video.date_published,
            "description": video.description, "thumbnail_path": video.thumbnail_path,
            "playlist_pos": video.playlist_pos, "url_video": video.url_video,
            "url_playlist_video": video.url_playlist_video, "thumbnails": video.thumbnails,
            "downloaded": video.downloaded, "search_item": video.search_item, "discarded": video.discarded,
            "vid_path": video.vid_path, "watched": video.watched, "watch_prio": video.watch_prio,
            "date_downloaded": video.date_downloaded}
