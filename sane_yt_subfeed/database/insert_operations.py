import threading

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video

lock = threading.Lock()

class UpdateVideosThread(threading.Thread):

    def __init__(self, video_list, update_existing=False):
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

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        lock.acquire()

        # start = default_timer()
        for video_d in self.video_list:
            db_video = db_session.query(Video).get(video_d.video_id)
            if db_video:
                if self.update_existing:
                    db_video.video_d_update(video_d)
                    db_session.commit()
            else:
                new_video = video_d.to_video()
                db_session.add(new_video)
                db_session.commit()
        db_session.remove()
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
        db_video = db_session.query(Video).get(self.video_d.video_id)
        if db_video:
            if self.update_existing:
                db_video.video_d_update(self.video_d)
                db_session.commit()
        else:
            new_video = self.video_d.to_video()
            db_session.add(new_video)
            db_session.commit()
        lock.release()
