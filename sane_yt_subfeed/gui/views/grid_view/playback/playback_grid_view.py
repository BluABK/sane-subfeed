from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView
from sane_yt_subfeed.gui.views.grid_view.playback.playback_grid_view_tile import PlaybackGridViewTile
from sane_yt_subfeed.log_handler import create_logger


class PlaybackGridView(GridView):

    def __init__(self, parent, root, main_model: MainModel):
        super().__init__(parent, root, main_model)
        self.logger = create_logger(__name__ + ".PlaybackGridView")
        self.root = root
        self.parent = parent

        self.main_model.grid_view_listener.playbackVideosChanged.connect(self.videos_changed)
        self.main_model.grid_view_listener.playbackVideosUpdated.connect(self.update_videos)

        self.logger.debug("Init grid")
        self.update_grid()
        self.logger.info("Initialized PlaybackGridView")

    def get_feed(self):
        subscription_feed = self.main_model.playview_videos
        return subscription_feed

    def new_tile(self, counter, video):
        return PlaybackGridViewTile(self, video, counter, self.clipboard, self.status_bar)

    def update_videos(self):
        for q_label, video in zip(self.q_labels.values(), self.main_model.playview_videos):
            q_label.set_video(video)
            self.q_labels[video.video_id] = q_label
        self.update_grid()
