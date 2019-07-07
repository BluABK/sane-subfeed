import os
import json

from PyQt5.QtCore import QObject, QFile, QTextStream
from PyQt5.QtWidgets import QStyleFactory, QMainWindow

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.absolute_paths import RESOURCES_PATH
from sane_yt_subfeed.handlers.config_handler import set_config, read_config

THEME_PATH = os.path.join(RESOURCES_PATH, 'themes')


class SaneThemeHandler(QObject):

    def __init__(self, main_window: QMainWindow):
        super(SaneThemeHandler, self).__init__()

        self.logger = create_logger(__name__)

        self.main_window = main_window

        self.themes = None
        self.styles = None

        self.current_theme = None
        self.current_theme_idx = 0
        self.current_style = None

        # Generate available themes
        self.generate_themes()

        # Generate available qstyles
        self.generate_styles()

        # Set the last used theme.
        last_theme = read_config('Theme', 'last_theme', literal_eval=False)
        if last_theme:
            self.logger.info("Using 'last used' theme: {}".format(last_theme))
            self.set_theme(read_config('Theme', 'last_theme', literal_eval=False))

        # Set the last used style.
        last_style = read_config('Theme', 'last_style', literal_eval=False)
        if last_style:
            self.logger.info("Using 'last used' style: {}".format(last_style))
            self.set_style(last_style)

        # Apply custom user theme mod overrides
        self.apply_user_overrides()

    @staticmethod
    def create_theme(path):
        """
        Creates a custom theme from relevant files and returns it as a dict

        metadata.json specification:
        {
          "name": "<name>",
          "version": "<version>",
          "author": "<author>",
          "description": "<description>",
          "variants":
          [
            {
              "name": "<name of variant 1>",
              "path": "<filename of variant 1>.qss"
              "platform_whitelist": <null or list containing linux|win32|cygwin||darwin>
            },
            {
              "name": "<name of variant 2>",
              "path": "<filename of variant 2>.qss"
              "platform_whitelist": <null or list containing linux|win32|cygwin|darwin>
            }, ....
          ]
        }

        :param: path:   Full path to the theme directory (in the themes directory).
        :return:
        """
        # Iterate through the files in the theme directory.
        files = []
        for file in os.listdir(path):
            # Only care about files, directories are irrelevant from this scope.
            if os.path.isfile(os.path.join(path, file)):
                files.append(file)

        # Parse metadata json (if one exists), if not make best guesses based on filenames.
        if 'metadata.json' in files:
            with open(os.path.join(path, 'metadata.json'), 'r') as infile:
                # Read metadata.json directly into a theme dict
                theme = json.load(infile)

                # Convert paths to absolute paths:
                for variant in theme['variants']:
                    variant['path'] = os.path.join(path, variant['path'])

        else:
            variants = []
            for file in files:
                if file.endswith('.qss'):
                    variant_path = file
                    variant_name, sep, extension = file.partition('.qss')

                    # Add variant to list of variants.
                    variants.append({'name': variant_name, 'path': os.path.join(path, variant_path),
                                     'platform_whitelist': None})

            # Create the theme dict based on best guesses.
            theme = {'name': os.path.split(path)[-1],
                     'version': None,
                     'author': None,
                     'description': None,
                     'variants': variants}

        return theme

    def generate_themes(self):
        """
        Generates a list of theme dicts and returns it.
        :return:
        """
        themes = []

        for theme_dir in os.listdir(THEME_PATH):
            full_theme_dir_path = os.path.join(THEME_PATH, theme_dir)
            if os.path.isdir(full_theme_dir_path):
                themes.append(self.create_theme(full_theme_dir_path))

        self.themes = themes

    def update_current_theme(self, theme):
        self.current_theme = theme
        set_config('Theme', 'last_theme', theme)

    def set_theme(self, theme):
        """
        Applies a QStyle or QStyleSheet to the QApplication
        :param theme:
        :return:
        """
        try:
            # Unset any previous stylesheets to avoid overlapping issues.
            if theme:
                self.set_theme_native()
            theme_file = QFile(theme)
            theme_file.open(QFile.ReadOnly | QFile.Text)
            theme_stream = QTextStream(theme_file)
            self.main_window.setStyleSheet(theme_stream.readAll())
            self.update_current_theme(theme)
            self.logger.info("Set theme (QStyleSheet): {}".format(theme))
        except Exception as exc:
            self.logger.error("Failed setting theme: {}".format(theme), exc_info=exc)

    def set_theme_native(self):
        """
        Reset the theme to default/native.
        :return:
        """
        self.set_theme(None)

    def cycle_themes(self):
        """
        Cycles through the available themes.
        :return:
        """
        if self.current_theme_idx >= len(self.themes) - 1:
            self.current_theme_idx = -1

        self.current_theme_idx += 1
        self.set_theme(self.themes[self.current_theme_idx])
        self.logger.info("Cycled to theme: '{}'".format(self.themes[self.current_theme_idx]))

    # Custom user mod themes (minor specific stylesheet overrides, as alternative to a full on QSS file)
    def set_custom_background_image(self, path):
        """
        Sets a custom image as the QToolbar background.
        :param path: path to image file
        :return:
        """
        # Set image as as a QSS property (border parm added as a workaround for certain platforms)
        self.main_window.setStyleSheet("background-image: url({});".format(path))
        self.logger.info("Set custom QMainWindow background image: {}".format(path))

    def set_custom_toolbar_image(self, path):
        """
        Sets a custom image as the QToolbar background.
        :param path: path to image file
        :return:
        """
        # Set image as as a QSS property (border parm added as a workaround for certain platforms)
        self.main_window.toolbar.setStyleSheet(
            "background: transparent; background-image: url({}); background-position: top right;".format(path))
        self.logger.info("Set custom toolbar image: {}".format(path))

    def set_custom_central_widget_image(self, path):
        """
        Sets a custom image as the central QWidget background.
        :param path: path to image file
        :return:
        """
        # Set image as as a QSS property (border parm added as a workaround for certain platforms)
        self.main_window.central_widget.setStyleSheet("background-image: url(:{}); border: 0px".format(path))
        self.logger.info("Set custom CentralWidget image: {}".format(path))

    def apply_user_overrides(self):
        """
        Applies custom user theme mod overrides
        :return:
        """
        if read_config('Theme', 'custom_image', literal_eval=False):
            self.set_custom_background_image(read_config('Theme', 'custom_image', literal_eval=False))
        if read_config('Theme', 'custom_toolbar_image', literal_eval=False):
            self.set_custom_toolbar_image(read_config('Theme', 'custom_toolbar_image',
                                                                    literal_eval=False))
        if read_config('Theme', 'custom_central_widget_image', literal_eval=False):
            self.set_custom_central_widget_image(
                read_config('Theme', 'custom_central_widget_image', literal_eval=False))

    def generate_styles(self):
        """
        Generates a list of available QStyles and returns it
        :return:
        """
        available_styles = {}
        qsf = QStyleFactory()

        # Populate the QStyle dict
        for style in qsf.keys():
            available_styles[style] = qsf.create(style)
        del qsf

        self.styles = available_styles

    def update_current_style(self, style):
        self.current_style = style
        set_config('Theme', 'last_style', style)

    def set_style(self, style):
        """
        Applies a QStyle or QStyleSheet to the QApplication
        :param style:
        :return:
        """
        try:
            self.main_window.setStyle(QStyleFactory.create(style))
            self.update_current_style(style)
            self.logger.info("Set style (QStylePlugin): {}".format(style))
        except Exception as exc:
            self.logger.error("Failed setting style: {}".format(style), exc_info=exc)
