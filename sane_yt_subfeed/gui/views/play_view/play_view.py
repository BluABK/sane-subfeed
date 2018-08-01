from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView


class PlayView(GridView):

    def __init__(self, parent, main_model, clipboard, status_bar):
        super().__init__(parent, main_model, clipboard, status_bar)

