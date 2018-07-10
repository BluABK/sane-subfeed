import threading
from timeit import default_timer

from sqlalchemy import text

from sane_yt_subfeed.database import video
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.orm import db_session, engine
from sane_yt_subfeed.database.video import Video

lock = threading.Lock()


def update_statement_full(db_video):
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
        search_item=db_video.search_item)


def get_video_by_id_stmt(video_d):
    return Video.__table__.select().where(text("video_id = '{}'".format(video_d.video_id)))


class UpdateVideosThread(threading.Thread):

    def __init__(self, video_list, update_existing=False, uniques_check=True):
        """
        Init GetUploadsThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        threading.Thread.__init__(self)
        self.video_list = video_list
        self.update_existing = update_existing
        self.uniques_check = uniques_check

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        if self.uniques_check:
            self.video_list = check_for_unique(self.video_list)

        lock.acquire()

        items_to_add = []
        items_to_update = []
        for video_d in self.video_list:
            stmt = get_video_by_id_stmt(VideoD.to_video(video_d))
            db_video = engine.execute(stmt).first()
            if db_video:
                if self.update_existing:
                    items_to_update.append(update_statement_full(db_video))
                else:
                    pass
            else:
                items_to_add.append(insert_item(video_d))
                if len(items_to_add) > 1000:
                    engine.execute(Video.__table__.insert(), items_to_add)
                    items_to_add = []

        if len(items_to_add) > 0:
            engine.execute(Video.__table__.insert(), items_to_add)
        if len(items_to_update) > 0:
            engine.execute(items_to_update)
        lock.release()


class UpdateVideo(threading.Thread):

    def __init__(self, video_d, update_existing=False):
        """
        Init GetUploadsThread
        :param video_d:
        """
        threading.Thread.__init__(self)
        self.video_d = video_d
        self.update_existing = update_existing

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        # start = default_timer()
        lock.acquire()
        stmt = get_video_by_id_stmt(VideoD.to_video(self.video_d))
        db_video = engine.execute(stmt).first()
        if db_video:
            if self.update_existing:
                engine.execute(update_statement_full(self.video_d))
            else:
                pass
        else:
            engine.execute(Video.__table__.insert(), insert_item(self.video_d))
        lock.release()


def check_for_unique(vid_list):
    print('vid_list before compare: {}'.format(len(vid_list)))
    compare_set = set()
    for vid in vid_list:
        if vid.video_id in compare_set:
            vid_list.remove(vid)
        else:
            compare_set.add(vid.video_id)
    print('vid_list after compare: {}'.format(len(vid_list)))
    return vid_list


def insert_item(video):
    return {"video_id": video.video_id, "channel_title": video.channel_title,
            'title': video.title, "date_published": video.date_published,
            "description": video.description, "thumbnail_path": video.thumbnail_path,
            "playlist_pos": video.playlist_pos, "url_video": video.url_video,
            "url_playlist_video": video.url_playlist_video, "thumbnails": video.thumbnails,
            "downloaded": video.downloaded, "search_item": video.search_item}
