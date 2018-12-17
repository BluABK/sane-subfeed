from PyQt5.QtCore import QObject

from sane_yt_subfeed import create_logger


class SaneHistoryItem(QObject):
    def __init__(self, parent, video, action=None, anti_action=None):
        QObject.__init__(self, parent=parent)
        self.logger = create_logger(__name__)
        self.root = parent.root
        self.parent = parent

        self.video = video
        self.action = action
        self.anti_action = anti_action

    def __str__(self):
        """
        Print
        :return:
        """
        return "{} - {} ({}) {} {}".format(self.video.channel_title, self.video.title,
                                           self.video.url_video, self.action, self.anti_action)

    def __log__(self):
        """
        Print-to-log
        :return:
        """
        self.logger.info(self.__str__())

    def log(self):
        """
        Public attribute/interface for print-to-log
        :return:
        """
        self.__log__()

    def delete(self):
        # Unset parent and get handled by GC
        self.parent = None

    def action(self):
        video = self.video
        action = self.action
        video.action()

    def anti_action(self):
        video = self.video
        anti_action = self.anti_action
        video.anti_action()
