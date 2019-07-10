import sys

from PySide2.QtWidgets import QApplication

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.controller.view_models import MainModel
from sane_yt_subfeed.gui.main_window.main_window import MainWindow
from sane_yt_subfeed.handlers.log_handler import create_logger


class Controller:

    def __init__(self):
        super().__init__()
        self.logger = create_logger(__name__)

    def run(self):
        # Enable Qt built-in High DPI scaling attribute (must be set *before* creating a QApplication!)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        app = QApplication(sys.argv)

        self.logger.info("Running Controller instance")
        vid_limit = read_config('Model', 'loaded_videos')

        start_with_stored_videos = read_config('Debug', 'start_with_stored_videos')

        main_model = MainModel([], vid_limit)
        if start_with_stored_videos:
            main_model.update_subfeed_videos_from_db()
        else:
            main_model.update_subfeed_videos_from_remote()

        main_model.update_playback_videos_from_db()

        self.logger.info(
            "Created MainModel: len(subscription_feed) = {}, vid_limit = {}".format(len(main_model.subfeed_videos),
                                                                                    vid_limit))

        self.logger.info("Created QApplication({})".format(sys.argv))
        window = MainWindow(app, main_model)
        window.show()
        self.logger.info("Executing Qt Application")
        app.exec_()
        self.logger.info("*** APPLICATION EXIT ***\n")
