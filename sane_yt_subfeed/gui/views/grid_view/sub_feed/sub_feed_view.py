from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView
from sane_yt_subfeed.gui.views.grid_view.sub_feed.sub_feed_tile import SubFeedTile
from sane_yt_subfeed.log_handler import create_logger


class SubFeedView(GridView):

    def __init__(self, parent, root, main_model: MainModel):
        self.logger = create_logger(__name__ + ".PlayView")
        self.logger.debug("Calling super")
        super().__init__(parent, root, main_model)

        self.main_model.grid_view_listener.hiddenVideosChanged.connect(self.videos_changed)

        self.logger.debug("Init grid")
        self.update_grid()
        self.logger.info("Initialized PlayView")

    def new_tile(self, counter, video):
        return SubFeedTile(self, video, counter, self.clipboard, self.status_bar)

    def get_feed(self):
        subscription_feed = self.main_model.filtered_videos
        return subscription_feed
