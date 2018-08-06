from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView
from sane_yt_subfeed.gui.views.grid_view.play_view.play_tile import PlayTile
from sane_yt_subfeed.log_handler import create_logger


class PlayView(GridView):

    def __init__(self, parent, root, main_model: MainModel):
        super().__init__(parent, root, main_model)
        self.logger = create_logger(__name__ + ".PlayView")

        self.main_model.grid_view_listener.downloadedVideosChanged.connect(self.videos_changed)

        self.logger.debug("Init grid")
        self.update_grid()
        self.logger.info("Initialized PlayView")

    def get_feed(self):
        subscription_feed = self.main_model.downloaded_videos
        return subscription_feed

    def new_tile(self, counter, video):
        return PlayTile(self, video, counter, self.clipboard, self.status_bar)
