import threading
from timeit import default_timer

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video

lock = threading.Lock()


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
        start = default_timer()
        if self.uniques_check:
            self.video_list = check_for_unique(self.video_list)
        time_elsapsed = default_timer() - start
        print("Comparison time: {}".format(time_elsapsed))

        lock.acquire()
        print('acquired lock')

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
        print('released lock')


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
        else:
            new_video = self.video_d.to_video()
            db_session.add(new_video)
        db_session.commit()
        db_session.remove()
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
