import threading
from timeit import default_timer

from sane_yt_subfeed.database.orm import db_session
from sane_yt_subfeed.database.video import Video


class UpdateVideosThreadSnippets(threading.Thread):

    def __init__(self, video_list):
        """
        Init GetUploadsThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        threading.Thread.__init__(self)
        self.video_list = video_list

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        # start = default_timer()
        # new_video_list = []
        for video in self.video_list:
            # new_video = Video(video.search_item)
            # new_video_list.append(new_video)
            db_video = db_session.query(Video).get(video.video_id)
            if db_video:
                # TODO update object
                pass
            else:
                db_session.add(video)
        db_session.commit()
        db_session.remove()
        # time_elsapsed = default_timer() - start
        # print("\nRun time: {}".format(time_elsapsed))

