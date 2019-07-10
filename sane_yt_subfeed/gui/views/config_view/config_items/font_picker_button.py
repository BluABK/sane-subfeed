from PySide2.QtGui import QFont
from PySide2.QtWidgets import QPushButton, QFontDialog

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.handlers.config_handler import read_config, set_config

FONT_WEIGHT_MAP = {'0': 'Thin', '12': 'ExtraLight', '18': 'Thi', '25': 'Light', '50': 'Regular', '54': 'Medium',
                   '62': 'ExtraCondensed', '63': 'DemiBold', '75': 'Bold', '81': 'ExtraBold', '87': 'Black'}
HUMAN_READABLE_KEYS = {'underline': 'Underline', 'strikeout': 'Strike out', 'fixed_pitch': 'Fixed pitch',
                       'raw_mode': 'RAW mode'}


class FontPickerButton(QPushButton):
    def __init__(self, parent, cfg_section, cfg_option, tooltip=None, actions=None, actions_kwargs=None):
        """
        A custom QPushButton that launches a QFontDialog.
        :param parent:          Parent ptr.
        :param cfg_section:     Config section.
        :param cfg_option:      Config Option.
        :param tooltip:         String to show on tooltip.
        :param actions:         Function to call when font is selected.
        :param actions_kwargs:  Keyword arguments (dict) to send in checked action calls.
        """
        super(QPushButton, self).__init__(parent=parent)
        self.parent = parent
        self.logger = create_logger(__name__)
        self.tooltip = tooltip
        self.cfg_section = cfg_section
        self.cfg_option = cfg_option
        self.current_font = QFont()
        self.current_font.fromString(read_config(self.cfg_section, self.cfg_option, literal_eval=False))
        self.update_info()

        self.clicked.connect(self.open_font_dialog)

    def weight_map_lookup(self, weight):
        """
        Checks if a weight exists in the font weight map,
        if not then it reports it and returns a fallback string.
        :param weight:
        :return:
        """
        if str(weight) in FONT_WEIGHT_MAP:
            return FONT_WEIGHT_MAP[str(weight)]
        else:
            self.logger.error("Umatched font weight: {}!".format(weight))
            return "UNDEFINED({})".format(weight)

    def map_font_str(self, font_str):
        """
        Maps a comma separated QFont.toString to a much more sensible dict, which it then returns.

        QFont.toString composition (comma separated, always in the following order):
            Family:      Font family name.
            Point size:  Point size of the font.
                -1 if the font size was specified in pixels.
            Pixel size:  Pixel size of the font if it was set with pixel size.
                -1 if the size was set with point size.
            Style hint:  Affects the {QFont}{font matching} algorithm. See QFont.StyleHint and QFont constants.
                 Style hints are used by the {QFont}{font matching} algorithm to find an appropriate default family
                 if a selected font family is not available.

                AnyStyle leaves the font matching algorithm to choose the family. This is the default.

                0 seems to be equivalent to Helvetica and 5 is AnyStyle.
            Weight:      Weight of the font (0-99), usually it's a predefined enum.
                Qt uses a weighting scale from 0 to 99 similar to, but not the same as, the scales used in Windows or
                CSS. A weight of 0 is ultralight, whilst 99 will be an extremely black.
            Style:       Style of the font (enum of the different styles of glyphs that are used to display text).
                Only covers the following types: Normal = 0, Italic = 1, Oblique = 2
            Underline:   Self-explanatory.
                0 if False, 1 if True.
            Strikeout:   Self-explanatory.
                0 if False, 1 if True.
            Fixed pitch: Fixed pitch value of the matched window system font.
                0 if False, 1 if True.

        Useful url:
            shorthand:              https://bit.ly/2XIjI5B
            raw (with linebreaks):  https://cep.xray.aps.anl.gov/software/qt4-x11-4.2.2-browser/
                                    d7/da1/class_q_font.html#5ab046d742a8538c2e2e50c2e03733ea

        :param font_str: A string in the form of QFont.toString().
        :return:
        """
        font_info = font_str.split(',')
        font_info_map = {'family':      str(font_info[0]),                      'point_size': int(font_info[1]),
                         'pixel_size':  float(font_info[2]),                    'style_hint': int(font_info[3]),
                         'weight':      self.weight_map_lookup(font_info[4]),   'style':      int(font_info[5]),
                         'underline':   bool(int(font_info[6])),                'strikeout':  bool(int(font_info[7])),
                         'fixed_pitch': bool(int(font_info[8])),                'raw_mode':   bool(int(font_info[9])),
                         'font_style': str(font_info[10])}

        return font_info_map

    def format_qfont_str(self, font_str):
        """
        Formats a QFont.toString to a more human readable string.
        :param font_str:
        :return:
        """
        # Map the string to a font info map/dict.
        f: dict = self.map_font_str(font_str)

        # Make a list of enabled setting keys.
        enabled_bools = []
        for key, value in f.items():
            if value is True:
                enabled_bools.append(HUMAN_READABLE_KEYS[key])

        # It is guaranteed to be either pt or px, so ternary works fine for this.
        pt_or_px = "{}pt.".format(f['point_size']) if f['point_size'] != -1 else "{}px.".format(f['pixel_size'])

        # Determine the enabled (boolean) settings:
        bools = []
        for boolean in enabled_bools:
            bools.append(boolean)
            bools.append(", ")

        if len(bools) > 0:
            # Strip trailing runaway comma-space delimiter
            bools = bools[:-1]

            # Wrap in parenthesis
            bools.insert(0, '(')
            bools.append(')')

        # Retval for weight (optional): " (" + f['weight'] + ")" if f['weight'] != f['font_style'] else "",

        return "{} ({}) {} {}".format(f['family'], f['font_style'], pt_or_px,
                                      "".join(bools) if not len(bools) == 0 else "")

    def update_info(self):
        """
        Update info (various text/labels etc).
        :return:
        """
        self.setText(self.format_qfont_str(self.current_font.toString()))
        if self.tooltip:
            self.setToolTip(self.tooltip)

    def open_font_dialog(self):
        """
        Opens a QFontDialog and updates current font and config with the choice (if any).
        :return:
        """
        font = QFont()
        font.fromString(read_config(self.cfg_section, self.cfg_option, literal_eval=False))
        font, ok = QFontDialog.getFont()

        # If user selected a font.
        if ok:
            # Update current font ref.
            self.current_font = font

            # Save selected font to config.
            set_config(self.cfg_section, self.cfg_option, font.toString())

            # Make button text reflect changes.
            self.update_info()

