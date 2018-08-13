import threading
import time
from random import randint

from sane_yt_subfeed.controller.database_listener import DatabaseListener
from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.engine_statements import update_video_statement_full, get_video_by_vidd_stmt, insert_item
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.orm import engine, db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.log_handler import create_logger

lock = threading.Lock()


def engine_execute_first(stmt):
    return engine.execute(stmt).first()


def engine_execute(stmt):
    engine.execute(stmt)


class UpdateVideosThread(threading.Thread):
    logger = create_logger(__name__ + ".UpdateVideosThread")


    def __init__(self, video_list, update_existing=False, uniques_check=True, finished_listeners=None):
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
        self.finished_listeners = finished_listeners
        self.db_id = randint(0, 9999)

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        DatabaseListener.static_instance.startWrite.emit(self.db_id)
        if self.uniques_check:
            self.video_list = check_for_unique(self.video_list)

        lock.acquire()
        items_to_add = []
        items_to_update = []
        for video_d in self.video_list:
            stmt = get_video_by_vidd_stmt(VideoD.to_video(video_d))
            db_video = engine.execute(stmt).first()
            if db_video:
                if self.update_existing:
                    engine.execute(update_video_statement_full(video_d))
                else:
                    pass
            else:
                items_to_add.append(insert_item(video_d))
                if len(items_to_add) > 1000:
                    engine.execute(Video.__table__.insert(), items_to_add)
                    items_to_add = []

        if len(items_to_add) > 0:
            engine.execute(Video.__table__.insert(), items_to_add)
        # FIXME: https://stackoverflow.com/questions/25694234/bulk-update-in-sqlalchemy-core-using-where
        # if len(items_to_update) > 0:
        #     engine.execute(items_to_update)
        lock.release()
        if self.finished_listeners:
            for listener in self.finished_listeners:
                listener.emit()
        DatabaseListener.static_instance.finishWrite.emit(self.db_id)


class UpdateVideo(threading.Thread):
    logger = create_logger(__name__ + ".UpdateVideo")

    def __init__(self, video_d, update_existing=False, finished_listeners=None):
        """
        Init GetUploadsThread
        :param video_d:
        """
        threading.Thread.__init__(self)
        self.finished_listeners = finished_listeners
        self.video_d = video_d
        self.update_existing = update_existing
        self.db_id = randint(0, 9999)

    # TODO: Handle failed requests
    def run(self):
        DatabaseListener.static_instance.startWrite.emit(self.db_id)
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        # self.logger.debug("Run")
        # start = default_timer()
        lock.acquire()
        stmt = get_video_by_vidd_stmt(VideoD.to_video(self.video_d))
        db_video = engine.execute(stmt).first()
        if db_video:
            if self.update_existing:
                engine.execute(update_video_statement_full(self.video_d))
            else:
                pass
        else:
            engine.execute(Video.__table__.insert(), insert_item(self.video_d))
        # print('Updated: {}'.format(self.video_d.title))
        lock.release()

        if self.finished_listeners:
            for listener in self.finished_listeners:
                listener.emit()
        DatabaseListener.static_instance.finishWrite.emit(self.db_id)


def check_for_unique(vid_list):
    compare_set = set()
    for vid in vid_list:
        if vid.video_id in compare_set:
            vid_list.remove(vid)
        else:
            compare_set.add(vid.video_id)
    return vid_list


def delete_sub_not_in_list(subs):
    delete_channels = db_session.query(Channel).filter(~Channel.id.in_(subs)).all()
    for channel in delete_channels:
        create_logger(__name__).warning("Deleting channel: {} - {}".format(channel.title, channel.id))
    stmt = Channel.__table__.delete().where(~Channel.id.in_(subs))
    engine.execute(stmt)