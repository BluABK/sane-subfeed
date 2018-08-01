import os
import subprocess
import timeit

from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.views.grid_view.grid_view import GridView


class PlayView(GridView):

    def __init__(self, parent, main_model, clipboard, status_bar):
        super().__init__(parent, main_model, clipboard, status_bar)

    def get_feed(self):
        subscription_feed = self.main_model.filtered_videos
        return subscription_feed

    def play(self, file_path, player="mpc-hc64"):
        play = subprocess.Popen([player, file_path])


    def do_walk(self, input_path):
        counter = 0

        start_time = timeit.default_timer()
        for root, dirs, files in os.walk(input_path):
            for name in files:
                if "bVfFvAoEL04" in name:
                    os.system("start \"{}\"".format(name))
                    print(name)
                counter += 1
        print(timeit.default_timer() - start_time)
        print(counter)