# PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QComboBox, QScrollArea

# Internal
from sane_yt_subfeed.config_handler import read_config, DEFAULTS_HOTKEYS, set_config
# import sane_yt_subfeed.gui.views.config_view.checkbox as checkbox
from sane_yt_subfeed.gui.views.config_view.config_items.line_edit import GenericLineEdit
from sane_yt_subfeed.gui.views.config_view.input_super import InputSuper
from sane_yt_subfeed.log_handler import create_logger


class HotkeysViewWidget(InputSuper):
    """
    Configuration widget
    """
    deco_l = "【"
    deco_r = "】"

    def __init__(self, parent, root, icon: QIcon=None):
        """
        A GUI Widget that shows hotkey bindings
        :param parent:
        :param clipboard:
        :param status_bar:
        """
        super().__init__(parent, root)
        if icon is not None:
            self.setWindowIcon(icon)  # FIXME: Icon won't set
        self.parent.setWindowTitle('Hotkey configuration')
        self.init_ui()
        self.populate_options()

    def init_ui(self):
        """
        Initialize UI
        :return:
        """
        self.logger.info("Initializing UI")

    def add_option_line_edit(self, description, cfg_section, cfg_option, cfg_validator=None):
        """
        Override of input super, to make LineEdit read only
        :param cfg_option:
        :param cfg_section:
        :param description:
        :return:
        """
        option = QLabel(description)
        value = GenericLineEdit(self, description, cfg_section, cfg_option, cfg_validator=cfg_validator)
        value.setReadOnly(True)
        self.layout.addWidget(option, self.offset, 0)
        self.layout.addWidget(value, self.offset, 1)
        self.offset += 1

    def populate_options(self):
        """
        Populate the layout with sections, options and (editable) values
        :return:
        """

        # Section [Global]
        self.add_section('{}Global{}'.format(self.deco_l, self.deco_r))
        self.preferences = self.add_option_line_edit('Preferences', 'Global', 'preferences')
        self.quitBinding = self.add_option_line_edit('Quit', 'Global', 'quit')
        self.copy_all_urls = self.add_option_line_edit('Copy all URLs', 'Global', 'copy_all_urls')
        self.refresh_feed = self.add_option_line_edit('Refresh feed', 'Global', 'refresh_feed')
        self.reload_subslist = self.add_option_line_edit('Reload subscriptions list', 'Global', 'reload_subslist')
        self.test_channels = self.add_option_line_edit('Test channels', 'Global', 'test_channels')
        self.manual_dir_search = self.add_option_line_edit('Manual dir search', 'Global', 'manual_dir_search')
        self.manual_thumb_dl = self.add_option_line_edit('Manual thumbnail download', 'Global', 'manual_thumb_dl')
        self.manual_db_grab = self.add_option_line_edit('Manual DB grab', 'Global', 'manual_db_grab')
        self.download_video_by_url = self.add_option_line_edit('Download Video by URL/ID dialog', 'Global',
                                                               'download_video_by_url')
        self.show_usage_history = self.add_option_line_edit('Show (usage) history', 'Global', 'show_usage_history')

        # Section [View]
        self.add_section('{}Views{}'.format(self.deco_l, self.deco_r))
        self.view_subfeed = self.add_option_line_edit('Subscription Feed (Grid)', 'View', 'subfeed')
        self.view_playback = self.add_option_line_edit('Playback Feed', 'View', 'playback')
        self.view_detailed_list = self.add_option_line_edit('Subscription feed (Detailed List)', 'View',
                                                            'detailed_list')
        self.view_subscriptions = self.add_option_line_edit('Subscriptions list', 'View', 'subscriptions')

        # Section [Subfeed]
        self.add_section('{}View: Subscription feed{}'.format(self.deco_l, self.deco_r))
        self.download = self.add_option_line_edit('Download', 'Subfeed', 'download')
        self.dismiss = self.add_option_line_edit('Dismiss', 'Subfeed', 'dismiss')

        # Section [PlayView]
        self.add_section('{}View: Playback feed{}'.format(self.deco_l, self.deco_r))
        self.prio_decrease = self.add_option_line_edit('Decrease priority', 'Playback', 'prio_decrease')
        self.mark_watched = self.add_option_line_edit('Mark watched', 'Playback', 'mark_watched')
        self.play_item = self.add_option_line_edit('Play video (implies: mark watched)', 'Playback', 'play')
        self.toggle_ascending_sort = self.add_option_line_edit('Toggle ascending sort', 'Playback', 'ascending_sort_toggle')

    def input_read_config_default(self, section, option):
        return "Not implemented"

    def input_read_config(self, section, option, literal_eval=True):
        return read_config(section, option, custom_ini="hotkeys", literal_eval=literal_eval)

    def output_set_config(self, section, option, value):
        set_config(section, option, value, custom_ini="hotkeys")
