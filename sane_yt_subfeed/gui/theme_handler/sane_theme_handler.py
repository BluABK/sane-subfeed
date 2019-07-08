import importlib
import os
import json

from PyQt5.QtCore import QObject, QFile, QTextStream
from PyQt5.QtWidgets import QStyleFactory, QMainWindow

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.absolute_paths import RESOURCES_PATH
from sane_yt_subfeed.handlers.config_handler import set_config, read_config

THEME_PATH = os.path.join(RESOURCES_PATH, 'themes')
COMPILED_QRC_LOADED = None
QRC_RESTART_MSG = "Compiled QRC assets are only loaded on startup. " \
                  "<br/><br/>" \
                  "If you pick a theme with such assets, " \
                  "you have to restart to load its assets (images and such). " \
                  "<br/><br/>" \
                  "This is due to overlapping issues when " \
                  "loading a second compiled QRC script which instantly" \
                  "<br/>" \
                  "makes Qt throw a SEGFAULT." \
                  "<br/><br/>"


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

            theme = self.get_theme_by_root_path(root_path)

            if theme is not None:
                # Load PyQt5 compiled QRC (if any)
                self.load_compiled_theme_resources(theme)

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

    def load_compiled_theme_resources(self, theme):
        """
        Loads a PyQt5 compiled QRC python script.

        NB: ONLY do this once (e.g. on startup) or you will get overlapping
        Qt resource imports leading to a lovely segmentation fault.

        :param theme:
        :return:
        """
        # Make sure this thing won't accidentally be run more than once (checker)
        global COMPILED_QRC_LOADED
        if COMPILED_QRC_LOADED:
            self.logger.critical("CAUTION: Attempted to import PyQt5 compiled resources, more than once! Bad idea...")
            return

        # Import PyQt5 compiled resources (if any), imports in the middle of the script, woohoo! (RIP PEP8)
        if theme['compiled_qrc'] is not None:
            # Partition out the file extension (for module loading).
            module, sep, junk = theme['compiled_qrc'].partition('.py')

            # Import the compiled QRC "module".
            compiled_resources = importlib.machinery.SourceFileLoader(module, os.path.join(
                theme['root_path'], theme['compiled_qrc'])).load_module()

            self.logger.info("Imported compiled QRC for theme '{}': {}".format(theme['name'], compiled_resources))

            # Make sure this thing won't accidentally be run more than once (setter)
            COMPILED_QRC_LOADED = theme

    def set_theme(self, theme_abs_path):
        """
        Applies a QStyle or QStyleSheet to the QApplication
        :param theme_abs_path: absolute filepath
        :return:
        """
        theme = None
        variant = None
        try:
            # Actions to take when theme_abs_path is not None
            if theme_abs_path:
                # Unset any previous stylesheets to avoid overlapping issues.
                self.set_theme_native()

                # Figure out the root and variant paths.
                root_path, variant_path = os.path.split(theme_abs_path)

                # Get the actual theme dict by given theme_abs_path
                theme = self.get_theme_by_root_path(root_path)

                # Get the variant
                variant = theme['variants'][self.get_variant_index_by_path(theme, variant_path)]

            theme_file = QFile(theme_abs_path)
            theme_file.open(QFile.ReadOnly | QFile.Text)
            theme_stream = QTextStream(theme_file)
            self.main_window.setStyleSheet(theme_stream.readAll())
            self.update_current_theme(theme_abs_path)
            if theme_abs_path:
                self.logger.info("Set theme: {} (variant: {})".format(theme['name'], variant['name']))
            else:
                self.logger.info("Reset theme to defaults.")
        except Exception as exc:
            self.logger.error("Failed setting theme: {}".format(theme), exc_info=exc)

        # Check that there exists a popup dialog action and that theme is not None
        if self.popup_dialog is not None and theme is not None:

            # Check if the new theme has a compiled QRC it wants loaded.
            if theme['compiled_qrc']:

                # Check if a compiled QRC has been loaded (to avoid NoneType in the following check).
                if COMPILED_QRC_LOADED is not None:

                    # Check if the QRC belongs to the current theme, if so no need to warn user.
                    if theme['name'] == COMPILED_QRC_LOADED['name']:
                        return

            # If compiled QRC either isn't loaded or is loaded but doesn't belong to the new theme.
            self.popup_dialog(title="Restart required for theme assets!", message=QRC_RESTART_MSG,
                              exclusive=True)

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
