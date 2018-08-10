# PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QComboBox, QScrollArea, QMainWindow

# Internal
from sane_yt_subfeed.config_handler import read_config, DEFAULTS_HOTKEYS, get_size
# import sane_yt_subfeed.gui.views.config_view.checkbox as checkbox
from sane_yt_subfeed.gui.views.config_view import checkbox, combobox
from sane_yt_subfeed.log_handler import create_logger


class HotkeysView(QScrollArea):

    def __init__(self, parent):
        super(HotkeysView, self).__init__(parent)

        self.parent = parent
        self.widget = HotkeysViewWidget(self, parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # self.resize(100, 100)


class HotkeysViewWidget(QWidget):
    """
    Configuration widget
    """
    offset = 0
    layout = None
    deco_l = "【"
    deco_r = "】"

    def __init__(self, parent, root):
        """
        A GUI Widget that shows hotkey bindings
        :param parent:
        :param clipboard:
        :param status_bar:
        """
        super(HotkeysViewWidget, self).__init__(parent)
        self.parent = parent
        self.root = root  # MainWindow
        self.logger = create_logger(__name__)
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
        # mismatch = get_size(custom_ini="hotkeys") - self.offset
        # if mismatch != 0:
        #     self.logger.warning("HotkeysView is missing {} entries!".format(mismatch))

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
        value = QCheckBox("(Default: {})".format(str(DEFAULTS_HOTKEYS[cfg_section][cfg_option])), self)
        value.setCheckState(2 if read_config(cfg_section, cfg_option, custom_ini='hotkeys') else 0)
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
        value = QLabel(str(DEFAULTS_HOTKEYS[cfg_section][cfg_option]))
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
            current_value = (read_config(cfg_section, cfg_option, custom_ini='hotkeys') - value_offset)

        else:
            current_value = items.index(read_config(cfg_section, cfg_option, custom_ini='hotkeys'))
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

        # Section [Global]
        self.add_section('{}Global{}'.format(self.deco_l, self.deco_r))
        self.preferences = self.add_option_inactive('Preferences', 'Global', 'preferences')
        self.quitBinding = self.add_option_inactive('Quit', 'Global', 'quit')
        self.copy_all_urls = self.add_option_inactive('Copy all URLs', 'Global', 'copy_all_urls')
        self.refresh_feed = self.add_option_inactive('Refresh feed', 'Global', 'refresh_feed')
        self.reload_subslist = self.add_option_inactive('Reload subscriptions list', 'Global', 'reload_subslist')
        self.test_channels = self.add_option_inactive('Test channels', 'Global', 'test_channels')
        self.manual_dir_search = self.add_option_inactive('Manual dir search', 'Global', 'manual_dir_search')
        self.manual_thumb_dl = self.add_option_inactive('Manual thumbnail download', 'Global', 'manual_thumb_dl')
        self.manual_db_grab = self.add_option_inactive('Manual DB grab', 'Global', 'manual_db_grab')

        # Section [View]
        self.add_section('{}Views{}'.format(self.deco_l, self.deco_r))
        self.view_subfeed = self.add_option_inactive('Subscription Feed (Grid)', 'View', 'subfeed')
        self.view_playback = self.add_option_inactive('Playback Feed', 'View', 'playback')
        self.view_detailed_list = self.add_option_inactive('Subscription feed (Detailed List)', 'View', 'detailed_list')
        self.view_subscriptions = self.add_option_inactive('Subscriptions list', 'View', 'subscriptions')

        # Section [Subfeed]
        self.add_section('{}View: Subscription feed{}'.format(self.deco_l, self.deco_r))
        self.download = self.add_option_inactive('Download', 'Subfeed', 'download')
        self.dismiss = self.add_option_inactive('Dismiss', 'Subfeed', 'dismiss')

        # Section [PlayView]
        self.add_section('{}View: Playback feed{}'.format(self.deco_l, self.deco_r))
        self.prio_decrease = self.add_option_inactive('Decrease priority', 'Playback', 'prio_decrease')
        self.mark_watched = self.add_option_inactive('Mark watched', 'Playback', 'mark_watched')
        self.play_item = self.add_option_inactive('Play video (implies: mark watched)', 'Playback', 'play')

