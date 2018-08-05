# PyQt5
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QComboBox

# Internal
from sane_yt_subfeed.config_handler import read_config, defaults, get_size
# import sane_yt_subfeed.gui.views.config_view.checkbox as checkbox
from sane_yt_subfeed.gui.views.config_view import checkbox, combobox
from sane_yt_subfeed.log_handler import create_logger


class ConfigView(QWidget):
    """
    Configuration widget
    """
    offset = 0
    layout = None
    deco_l = "【"
    deco_r = "】"

    # Options tied to listeners or similar
    launch_gui = None
    hide_downloaded_vids = None
    debug_toggle = None
    cache_subs = None
    start_with_cached_vids = None
    use_playlist_items = None
    disable_tooltips = None
    disable_tqdm = None
    use_tests = None
    force_dl_best_thumb = None

    def __init__(self, parent):
        """
        A GUI Widget that reads and sets config.ini settings
        :param parent:
        :param clipboard:
        :param status_bar:
        """
        super(ConfigView, self).__init__(parent)
        self.logger = create_logger("ConfigView")
        self.root = parent  # MainWindow
        self.clipboard = self.root.clipboard
        self.status_bar = self.root.status_bar
        self.init_ui()

    def init_ui(self):
        """
        Initialize UI
        :return:
        """
        self.logger.info("Initializing UI")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.populate_options()
        mismatch = get_size() - self.offset
        if mismatch != 0:
            self.logger.warning("ConfigView is missing {} entries!".format(mismatch))

    def add_section(self, name):
        """
        Add a section to the ConfigView layout and increment grid offset.
        :return:
        """
        self.layout.addWidget(QLabel(name), self.offset, 0)
        self.offset += 1

    def add_option_checkbox(self, description, cfg_section, cfg_option, value_listener):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param cfg_option:
        :param cfg_section:
        :param value_listener:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = QCheckBox("(Default: {})".format(str(defaults[cfg_section][cfg_option])), self)
        value.setCheckState(2 if read_config(cfg_section, cfg_option) else 0)
        value.stateChanged.connect(value_listener)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_inactive(self, description, cfg_section, cfg_option):
        """
        Add an option w/ UNEDITABLE value to the ConfigView layout and increment the grid offset.
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = QLabel(str(defaults[cfg_section][cfg_option]))
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def add_option_combobox(self, description, cfg_section, cfg_option, value_listener, items, numeric=True):
        """
        Add an option w/ value to the ConfigView layout and increment the grid offset.
        :param numeric:
        :param items:
        :param cfg_option:
        :param cfg_section:
        :param value_listener:
        :param description:
        :return:
        """
        if numeric:
            items = [str(i) for i in items]
            if items[0] == 'Disabled':
                value_offset = -1
            elif int(items[0]) == 0:
                value_offset = 0
            elif int(items[0]) == 1:
                value_offset = 1
            else:
                value_offset = 1
            current_value = (read_config(cfg_section, cfg_option) - value_offset)

        else:
            current_value = items.index(read_config(cfg_section, cfg_option))
        option = QLabel(description)
        # value = QCheckBox("(Default: {})".format(str(defaults[cfg_section][cfg_option])), self)
        value = QComboBox()
        value.addItems(items)
        value.setCurrentIndex(current_value)
        value.activated.connect(value_listener)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

        return value  # Needed for connected listeners etc

    def populate_options(self):
        """
        Populate the layout with sections, options and (editable) values
        :return:
        """
        combox_w_disabled = list(range(-1, 1000))
        combox_w_disabled[0] = 'Disabled'
        thumb_qualities = ['maxres', 'standard', 'high', 'medium', 'default']
        tt_font_sizes = ['h1', 'h2', 'h3', 'h4', 'h5', 'p']

        # Section [Gui]
        self.add_section('{}GUI{}'.format(self.deco_l, self.deco_r))
        self.launch_gui = self.add_option_checkbox('Launch GUI', 'Gui', 'launch_gui', checkbox.gui_launch_gui)
        self.hide_downloaded_vids = self.add_option_checkbox('Hide downloaded videos from feed', 'Gui',
                                                             'hide_downloaded', checkbox.gui_hide_downloaded)
        self.add_option_combobox('Grid view X', 'Gui', 'grid_view_x', combobox.gui_grid_view_x, list(range(1, 100)))
        self.add_option_combobox('Grid view Y', 'Gui', 'grid_view_y', combobox.gui_grid_view_y, list(range(1, 100)))
        self.add_option_checkbox('Grey background on old (1d+) videos', 'Gui', 'grey_old_videos',
                                 checkbox.gui_grey_old_videos)
        self.add_option_checkbox('Enable grid resizing', 'Gui', 'enable_grid_resize', checkbox.gui_enable_grid_resize)

        self.add_option_combobox('\tGrid tile height (px)', 'Gui', 'tile_pref_height',
                                 combobox.gui_tile_pref_height, list(range(1, 1000)))
        self.add_option_combobox('\tGrid tile width (px)', 'Gui', 'tile_pref_width',
                                 combobox.gui_tile_pref_width, list(range(1, 1000)))
        self.add_option_checkbox('Embed thumbnails in tooltips', 'Gui', 'tooltip_pictures',
                                 checkbox.gui_tooltip_pictures)
        self.add_option_combobox('\tTooltip picture width', 'Gui', 'tooltip_picture_width', combobox.gui_tooltip_picture_width, list(range(1, 1000)))
        self.add_option_combobox('\tTooltip picture height', 'Gui', 'tooltip_picture_height', combobox.gui_tooltip_picture_height, list(range(1, 1000)))
        self.add_option_combobox('\tTooltip picture font size', 'Gui', 'tooltip_picture_size', combobox.gui_tooltip_picture_size, tt_font_sizes, numeric=False)
        self.add_option_checkbox('Keep Aspect Ratop on resized thumbnails', 'Gui', 'keep_thumb_ar',
                                 checkbox.gui_keep_thumb_ar)

        # Section [Debug]
        self.add_section('{}Debug{}'.format(self.deco_l, self.deco_r))
        self.debug_toggle = self.add_option_checkbox('Debug prints', 'Debug', 'debug', checkbox.debug_toggle)
        self.cache_subs = self.add_option_checkbox('Cache subscriptions', 'Debug', 'cached_subs',
                                                   checkbox.debug_cached_subs)
        self.start_with_cached_vids = self.add_option_checkbox('Start with cached videos', 'Debug',
                                                               'start_with_stored_videos',
                                                               checkbox.debug_start_with_stored_videos)
        self.add_option_combobox('Channel limit', 'Debug', 'channels_limit', combobox.debug_channels_limit,
                                 combox_w_disabled)
        self.use_playlist_items = self.add_option_checkbox('Use playlistItems', 'Debug', 'use_playlistitems',
                                                           checkbox.debug_use_playlistitems)
        self.disable_tooltips = self.add_option_checkbox('Disable tooltips', 'Debug', 'disable_tooltips',
                                                         checkbox.debug_disable_tooltips)
        self.disable_tqdm = self.add_option_checkbox('Disable tqdm (cli)', 'Debug', 'disable_tqdm',
                                                     checkbox.debug_disable_tqdm)

        # Section [Requests]
        self.add_section('{}Requests{}'.format(self.deco_l, self.deco_r))
        self.use_tests = self.add_option_checkbox('Use tests', 'Requests', 'use_tests', checkbox.requests_use_tests)
        self.add_option_combobox('Missed video limit', 'Requests', 'miss_limit', combobox.requests_miss_limit,
                                 list(range(0, 201)))
        self.add_option_combobox('Test pages', 'Requests', 'test_pages', combobox.requests_test_pages,
                                 list(range(0, 201)))

        # Section [Thumbnails]
        self.add_section('{}Thumbnails{}'.format(self.deco_l, self.deco_r))
        self.force_dl_best_thumb = self.add_option_checkbox('Force download best quality, based on prioritised list',
                                                            'Thumbnails', 'force_download_best',
                                                            checkbox.thumbnails_force_download_best)
        self.add_option_combobox('1. Priority', 'Thumbnails', '0', combobox.thumbnails_priority_1, thumb_qualities,
                                 numeric=False)
        self.add_option_combobox('2. Priority', 'Thumbnails', '1', combobox.thumbnails_priority_2, thumb_qualities,
                                 numeric=False)
        self.add_option_combobox('3. Priority', 'Thumbnails', '2', combobox.thumbnails_priority_3, thumb_qualities,
                                 numeric=False)
        self.add_option_combobox('4. Priority', 'Thumbnails', '3', combobox.thumbnails_priority_4, thumb_qualities,
                                 numeric=False)
        self.add_option_combobox('5. Priority', 'Thumbnails', '4', combobox.thumbnails_priority_5, thumb_qualities,
                                 numeric=False)

        # Section [Threading]
        self.add_section('{}Threading{}'.format(self.deco_l, self.deco_r))
        self.add_option_combobox('Image/thumbnail download thread limit', 'Threading', 'img_threads',
                                 combobox.threading_img_threads, list(range(1, 1001)))
