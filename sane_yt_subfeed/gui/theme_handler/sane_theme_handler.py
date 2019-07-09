import importlib
import os
import json

from PyQt5.QtCore import QObject, QFile, QTextStream
from PyQt5.QtWidgets import QStyleFactory, QMainWindow

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.absolute_paths import RESOURCES_PATH
from sane_yt_subfeed.handlers.config_handler import set_config, read_config

THEME_PATH = os.path.join(RESOURCES_PATH, 'themes')

# If not None, holds the theme dict related to the currently loaded QRC.
COMPILED_QRC_THEME = None
# If not None, holds the currently loaded QRC module.
COMPILED_QRC_MODULE = None


class SaneThemeHandler(QObject):

    def __init__(self, main_window: QMainWindow, popup_dialog=None):
        super(SaneThemeHandler, self).__init__()

        self.logger = create_logger(__name__)

        self.main_window = main_window
        self.popup_dialog = popup_dialog

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

            # Determine the theme dict based on the absolute path to its variant
            root_path, variant_path = os.path.split(read_config('Theme', 'last_theme', literal_eval=False))

            # Retrieve the respective theme dict.
            theme = self.get_theme_by_root_path(root_path)

            if theme is not None:
                # Set the theme
                self.set_theme(last_theme)
            else:
                self.logger.error("Unable to restore last theme (INVALID: NoneType): {}".format(last_theme))

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
          "compiled_qrc": "resources.py",
          "variants":
          [
            {
              "name": "<name of variant 1>",
              "path": "<filename of variant 1>.qss"
              "platform_whitelist": <null or list containing linux|win32|cygwin|darwin>
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
        compiled_qrc = None

        # Iterate through the files in the theme directory.
        files = []
        for file in os.listdir(path):
            # Only care about files, directories are irrelevant from this scope.
            if os.path.isfile(os.path.join(path, file)):
                # Store info about any required compiled qrc file (basic guess by name, best if user specifies in JSON.
                if file.endswith('.py') and 'resources' in file:
                    compiled_qrc = file

                files.append(file)

        # Parse metadata json (if one exists), if not make best guesses based on filenames.
        if 'metadata.json' in files:
            with open(os.path.join(path, 'metadata.json'), 'r') as infile:
                # Read metadata.json directly into a theme dict
                theme = json.load(infile)

                # Convert paths to absolute paths:
                for variant in theme['variants']:
                    variant['path'] = os.path.join(path, variant['path'])

                # Add the root path to the theme directory (required for compiled QRC)
                theme['root_path'] = path

                # Add entry about whether or not the theme requires compiled QRC (if it does not already exist)
                if 'compiled_qrc' not in theme:
                    theme['compiled_qrc'] = compiled_qrc

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
                     'variants': variants,
                     'root_path': path,
                     'compiled_qrc': compiled_qrc}

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

    def update_current_theme(self, theme_abs_path):
        """
        Saves the current theme variant to config and self (using its absolute path)
        :param theme_abs_path:
        :return:
        """
        self.current_theme = theme_abs_path
        set_config('Theme', 'last_theme', theme_abs_path)

    def get_theme_by_root_path(self, path):
        """
        Takes an absolute path to a theme (and its variant) QSS file
        and returns the respective assembled theme dict.

        :param path:    absolute path to a .qss file
        :return:        theme dict
        """
        for theme in self.themes:
            if theme['root_path'] == path:

                return theme

    @staticmethod
    def get_variant_index_by_path(theme, variant_path):
        """
        Takes a theme dict and a variant path (usually 'filename.qss')
        and returns the index of the variant in theme['variants].

        :param theme:           dict
        :param variant_path:    string
        :return:                integer
        """
        for index in range(len(theme['variants'])):
            if theme['variants'][index]['path'] == os.path.join(theme['root_path'], variant_path):

                return index

    def unload_compiled_qrc(self):
        """
        Attempts to unload a compiled QRC module, if any exception occurs raise it to avoid the SEGFAULT of Doom™.
        :return:
        """
        global COMPILED_QRC_MODULE, COMPILED_QRC_THEME

        # Unload the currently loaded PyQt5 compiled QRC module and its resources.
        self.logger.info("Unloading currently loaded PyQt5 compiled QRC module "
                         "for theme '{}': {}".format(COMPILED_QRC_THEME['name'], COMPILED_QRC_MODULE))
        try:
            COMPILED_QRC_MODULE.qCleanupResources()
        except Exception as abort_before_segfault:
            self.logger.critical("Unable to unload currently loaded compiled QRC module, "
                                 "Aborting in order to not cause a SEGFAULT!", exc_info=abort_before_segfault)

            raise abort_before_segfault

    def load_compiled_qrc(self, theme):
        """
        Loads a PyQt5 compiled QRC python script.

        NB: PyQt can only handle a single compiled QRC module at a time,
        if you load more than one Qt will SEGFAULT. So make sure to unload
        the current one first.

        :param theme: theme dict
        :return:
        """
        # If a compiled QRC is already loaded, unload it or suffer the consequences; a swift SEGFAULT.
        global COMPILED_QRC_THEME, COMPILED_QRC_MODULE
        if COMPILED_QRC_MODULE:
            self.unload_compiled_qrc()

        # Partition out the file extension (for module loading).
        module, sep, junk = theme['compiled_qrc'].partition('.py')

        # Import the PyQt5 compiled QRC module. Imports happening in the middle of the script, RIP PEP8 =/
        self.logger.info("Loading PyQt5 compiled QRC module for theme '{}': {}".format(theme['name'], COMPILED_QRC_THEME))
        COMPILED_QRC_MODULE = importlib.machinery.SourceFileLoader(module, os.path.join(
            theme['root_path'], theme['compiled_qrc'])).load_module()

        # Store which theme the loaded compiled QRC resources belong to.
        COMPILED_QRC_THEME = theme

    def set_theme(self, theme_abs_path):
        """
        Applies a QStyle or QStyleSheet to the QApplication
        :param theme_abs_path: absolute filepath
        :return:
        """
        theme = None
        variant = None

        # If given NoneType, reset to defaults.
        if theme_abs_path is None:
            self.clear_current_theme()
            return

        try:
            # Unset any previous stylesheets to avoid overlapping issues.
            self.clear_current_theme()

            # Figure out the root and variant paths.
            root_path, variant_path = os.path.split(theme_abs_path)

            # Get the actual theme dict by given theme_abs_path
            theme = self.get_theme_by_root_path(root_path)

            # Get the variant
            variant = theme['variants'][self.get_variant_index_by_path(theme, variant_path)]

            # Load PyQt5 compiled QRC (if any)
            if theme['compiled_qrc'] is not None:
                self.load_compiled_qrc(theme)

            theme_file = QFile(theme_abs_path)
            theme_file.open(QFile.ReadOnly | QFile.Text)
            theme_stream = QTextStream(theme_file)

            self.main_window.setStyleSheet(theme_stream.readAll())

            self.update_current_theme(theme_abs_path)

            self.logger.info("Set theme: {} (variant: {})".format(theme['name'], variant['name']))
        except Exception as exc:
            self.logger.error("Failed setting theme: {}".format(theme), exc_info=exc)

    def clear_current_theme(self):
        """
        Reset the theme to default/native.
        :return:
        """
        self.main_window.setStyleSheet(None)
        self.logger.info("Cleared theming.")

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
            self.logger.info("Set style: {}".format(style))
        except Exception as exc:
            self.logger.error("Failed setting style: {}".format(style), exc_info=exc)
