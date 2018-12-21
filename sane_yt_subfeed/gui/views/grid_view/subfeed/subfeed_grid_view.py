from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView
from sane_yt_subfeed.gui.views.grid_view.subfeed.subfeed_grid_view_tile import SubfeedGridViewTile
from sane_yt_subfeed.log_handler import create_logger


class SubfeedGridView(GridView):

    def __init__(self, parent, root, main_model: MainModel):
        super().__init__(parent, root, main_model)
        self.logger = create_logger(__name__ + ".SubfeedGridView")

        self.main_model.subfeed_grid_view_listener.videosChanged.connect(self.videos_changed)
        self.main_model.subfeed_grid_view_listener.videosUpdated.connect(self.update_videos)
        self.main_model.subfeed_grid_view_listener.redrawVideos.connect(self.redraw_videos)

        self.logger.debug("Init grid")
        self.update_grid()
        self.logger.info("Initialized PlaybackGridView")

    def new_tile(self, counter, video):
        return SubfeedGridViewTile(self, video, counter, self.clipboard, self.status_bar)

    def get_feed(self):
        subscription_feed = self.main_model.subfeed_videos
        return subscription_feed

    def update_videos(self):
        for q_label, video in zip(self.q_labels.values(), self.main_model.subfeed_videos):
            q_label.set_video(video)
            self.q_labels[video.video_id] = q_label
        self.update_grid()
