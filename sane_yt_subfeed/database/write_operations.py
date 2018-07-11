import threading

from sane_yt_subfeed.database.detached_models.video_d import VideoD
from sane_yt_subfeed.database.engine_statements import update_video_statement_full, get_video_by_id_stmt, insert_item
from sane_yt_subfeed.database.orm import engine
from sane_yt_subfeed.database.video import Video

lock = threading.Lock()


def engine_execute_first(stmt):
    return engine.execute(stmt).first()

def engine_execute(stmt):
    engine.execute(stmt)


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
                    items_to_update.append(update_video_statement_full(db_video))
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
        # lock.acquire()
        stmt = get_video_by_id_stmt(VideoD.to_video(self.video_d))
        db_video = engine.execute(stmt).first()
        if db_video:
            if self.update_existing:
                engine.execute(update_video_statement_full(self.video_d))
            else:
                pass
        else:
            engine.execute(Video.__table__.insert(), insert_item(self.video_d))
        print('Updated: {}'.format(self.video_d.title))
        # lock.release()


def check_for_unique(vid_list):
    compare_set = set()
    for vid in vid_list:
        if vid.video_id in compare_set:
            vid_list.remove(vid)
        else:
            compare_set.add(vid.video_id)
    return vid_list


