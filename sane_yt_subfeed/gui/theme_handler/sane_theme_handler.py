import importlib
import os

from PyQt5.QtCore import QObject, QFile, QTextStream
from PyQt5.QtWidgets import QStyleFactory, QMainWindow

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.absolute_paths import RESOURCES_PATH
from sane_yt_subfeed.gui.theme_handler.sane_theme import SaneTheme
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
        # Theme lookup where key is the absolute path to variant filename and value is the corresponding SaneTheme.
        self.themes_by_variant_absolute_path = {}
        self.styles = None

        self.current_theme = None
        self.current_theme_idx = 0
        self.current_style = None

        # Generate available themes and styles
        self.generate_themes()
        self.generate_styles()

        # Set the last used theme.
        variant_absolute_path = read_config('Theme', 'last_theme', literal_eval=False)
        if variant_absolute_path:
            self.logger.info("Using 'last used' theme: {}".format(variant_absolute_path))

            # Retrieve the respective theme dict.
            theme = self.get_theme_by_variant_absolute_path(variant_absolute_path)

            if theme is not None:
                # Set the theme
                self.set_theme(variant_absolute_path)
            else:
                self.logger.error("Unable to restore last theme (INVALID: NoneType): {}".format(variant_absolute_path))

        # Set the last used style.
        last_style = read_config('Theme', 'last_style', literal_eval=False)
        if last_style:
            self.logger.info("Using 'last used' style: {}".format(last_style))
            self.set_style(last_style)

        # Apply custom user theme mod overrides
        self.apply_user_overrides()

    def generate_themes(self):
        """
        Generates a list of theme dicts and returns it.
        :return:
        """
        # Clear any current theme entries to avoid dupes.
        self.themes = []
        self.themes_by_variant_absolute_path = {}

        for theme_dir in os.listdir(THEME_PATH):
            theme_dir_absolute_path = os.path.join(THEME_PATH, theme_dir)
            if os.path.isdir(theme_dir_absolute_path):
                new_theme = SaneTheme(theme_dir_absolute_path, theme_handler=self)
                self.logger.debug9(new_theme.__dict__)
                self.themes.append(new_theme)
                for variant in new_theme.variants:
                    self.themes_by_variant_absolute_path[variant['file_absolute_path']] = new_theme

    def update_current_theme(self, theme_abs_path):
        """
        Saves the current theme variant to config and self (using its absolute path)
        :param theme_abs_path:
        :return:
        """
        self.current_theme = theme_abs_path
        set_config('Theme', 'last_theme', theme_abs_path)

    def get_theme_by_variant_absolute_path(self, variant_absolute_path):
        """
        Takes an absolute path to a theme variant QSS file
        and returns the respective assembled theme dict.

        :param variant_absolute_path:    Absolute path to a .qss theme variant file.
        :return:                         SaneTheme or NoneType.
        """
        if variant_absolute_path in self.themes_by_variant_absolute_path:
            return self.themes_by_variant_absolute_path[variant_absolute_path]
        else:
            return None

    @staticmethod
    def get_variant_index_by_variant_absolute_path(theme, variant_absolute_path):
        """
        Takes a SaneTheme and an absolute path to a theme variant filename
        and returns the index of the variant in theme['variants].

        :param theme:                   SaneTheme
        :param variant_absolute_path:   str
        :return:                        int index of variant or None
        """
        for index in range(len(theme.variants)):
            if theme.variants[index]['file_absolute_path'] == variant_absolute_path:
                return index

        return None

    @staticmethod
    def get_variant_index_by_filename(theme, variant_filename):
        """
        Takes a SaneTheme and a variant path (usually 'filename.qss')
        and returns the index of the variant in theme['variants].

        :param theme:               SaneTheme
        :param variant_filename:    str
        :return:                    int index of variant or None
        """
        for index in range(len(theme.variants)):
            if theme.variants[index]['file_absolute_path'] == os.path.join(theme.theme_dir_absolute_path,
                                                                           variant_filename):
                return index
            else:
                return None

    def unload_compiled_qrc(self):
        """
        Attempts to unload a compiled QRC module, if any exception occurs raise it to avoid the SEGFAULT of Doom™.
        :return:
        """
        global COMPILED_QRC_MODULE, COMPILED_QRC_THEME

        # Unload the currently loaded PyQt5 compiled QRC module and its resources.
        self.logger.info("Unloading currently loaded PyQt5 compiled QRC module "
                         "for theme '{}': {}".format(COMPILED_QRC_THEME.name, COMPILED_QRC_MODULE))
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

        # Import the PyQt5 compiled QRC module. Imports happening in the middle of the script, RIP PEP8 =/
        COMPILED_QRC_MODULE = importlib.machinery.SourceFileLoader(theme.compiled_qrc_modulename, os.path.join(
            theme.theme_dir_absolute_path, theme.compiled_qrc_filename)).load_module()

        # Store which theme the loaded compiled QRC resources belong to.
        COMPILED_QRC_THEME = theme

        self.logger.info("Loaded PyQt5 compiled QRC module for theme '{}': {}".format(theme.name, COMPILED_QRC_THEME))

    def set_theme(self, variant_absolute_path):
        """
        Applies a QStyle or QStyleSheet to the QApplication
        :param variant_absolute_path: absolute filepath
        :return:
        """
        theme = None
        variant = None

        # If given NoneType, reset to defaults.
        if variant_absolute_path is None:
            self.clear_current_theme()
            return

        try:
            # Unset any previous stylesheets to avoid overlapping issues.
            self.clear_current_theme()

            # Get the actual SaneTheme by given variant_absolute_path
            theme = self.get_theme_by_variant_absolute_path(variant_absolute_path)

            # Get the variant
            variant = theme.variants[self.get_variant_index_by_variant_absolute_path(theme, variant_absolute_path)]

            # Load PyQt5 compiled QRC (if any)
            if theme.compiled_qrc_filename is not None:
                self.load_compiled_qrc(theme)

            theme_file = QFile(variant_absolute_path)
            theme_file.open(QFile.ReadOnly | QFile.Text)
            theme_stream = QTextStream(theme_file)

            self.main_window.setStyleSheet(theme_stream.readAll())

            self.update_current_theme(variant_absolute_path)

            self.logger.info("Set theme: {} (variant: {})".format(theme.name, variant['name']))
        except Exception as exc:
            self.logger.error("Failed setting theme: {}".format(theme), exc_info=exc)

    def clear_current_theme(self):
        """
        Reset the theme to default/native.
        :return:
        """
        self.main_window.setStyleSheet(None)
        self.logger.debug("Cleared theming.")

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
