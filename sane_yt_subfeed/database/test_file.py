import sqlite3

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.database.engine_statements import update_video_statement_full, get_channel_by_id_stmt, \
    get_video_by_id_stmt

engine = create_engine('sqlite:///../resources/permanents.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
PermanentBase = declarative_base()
PermanentBase.query = db_session.query_property()


def init_sqlite3(dbname):
    conn = sqlite3.connect(dbname)
    conn.commit()
    return conn


def run():
    video_item = {'kind': 'youtube#searchResult', 'etag': '"XI7nbFXulYBIpL0ayR_gDh3eu1k/rrGI6j0VT4vX91p6eQyuqFQjf8M"',
                  'id': {'kind': 'youtube#video', 'videoId': '8NG1PEFceG0'},
                  'snippet': {'publishedAt': '2017-06-22T19:26:41.000Z', 'channelId': 'UCzORJV8l3FWY4cFO8ot-F2w',
                              'title': '[Vinesauce] Vinny - The Legend of Zelda: Clips of the Wild',
                              'description': 'A compilation of user-created Twitch clips from Breath of the Wild! Streamed live on Vinesauce. Check out my other youtube channel for full streams.',
                              'thumbnails': {
                                  'default': {'url': 'https://i.ytimg.com/vi/8NG1PEFceG0/default.jpg', 'width': 120,
                                              'height': 90},
                                  'medium': {'url': 'https://i.ytimg.com/vi/8NG1PEFceG0/mqdefault.jpg', 'width': 320,
                                             'height': 180},
                                  'high': {'url': 'https://i.ytimg.com/vi/8NG1PEFceG0/hqdefault.jpg', 'width': 480,
                                           'height': 360}}, 'channelTitle': 'vinesauce',
                              'liveBroadcastContent': 'none'}}

    channel_item = {"publishedAt": "2015-01-09T12:46:03.000Z", "title": "OfficialNerdCubed",
                    "description": "Recommending good games every Monday and Wednesday. Going strange every Saturday.",
                    "resourceId": {"kind": "youtube#channel", "channelId": "UCKab3hYnOoTZZbEUQBMx-ww"},
                    "channelId": "UCv5TbAM7zHQOoDr0fw2Cy8w", "thumbnails": {"default": {
            "url": "https://yt3.ggpht.com/-2AuBRBi8yE8/AAAAAAAAAAI/AAAAAAAAAAA/PsaY8p1aJ2U/s88-c-k-no-mo-rj-c0xffffff/photo.jpg"},
            "medium": {
                "url": "https://yt3.ggpht.com/-2AuBRBi8yE8/AAAAAAAAAAI/AAAAAAAAAAA/PsaY8p1aJ2U/s240-c-k-no-mo-rj-c0xffffff/photo.jpg"},
            "high": {
                "url": "https://yt3.ggpht.com/-2AuBRBi8yE8/AAAAAAAAAAI/AAAAAAAAAAA/PsaY8p1aJ2U/s800-c-k-no-mo-rj-c0xffffff/photo.jpg"}}}

    channel = Channel(channel_item, 'UUv5TbAM7zHQOoDr0fw2Cy8w')
    video = Video(video_item)
    insrt_txt = {"video_id": video.video_id, "channel_title": video.channel_title,
                 'title': video.title, "date_published": video.date_published,
                 "description": video.description, "thumbnail_path": video.thumbnail_path,
                 "playlist_pos": video.playlist_pos, "url_video": video.url_video,
                 "url_playlist_video": video.url_playlist_video, "thumbnails": video.thumbnails,
                 "downloaded": video.downloaded, "search_item": video.search_item}
    # stmt_1 = Video.__table__.insert(), [insrt_txt]
    # engine.execute(Video.__table__.insert(), [insrt_txt])
    # stmt = update_statement_full(video)
    # stmt = get_video_by_id_stmt(video)
    # # stmt = Video.__table__.select('video.video_id').where(text("video_id = '{}'".format(video.video_id)))
    # # print(db_session.execute(stmt).first())
    # print(engine.execute(stmt).first())
    # video2 = engine.execute(Video.__table__.select(Video.title).where('video_id' == video.video_id).limit(1))
    stmt = get_channel_by_id_stmt(channel)
    print(engine.execute(stmt).first())

if __name__ == '__main__':
    run()
