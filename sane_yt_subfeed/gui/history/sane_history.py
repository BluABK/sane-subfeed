from PyQt5.QtCore import QObject

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.gui.history.sane_history_item import SaneHistoryItem


class SaneHistory(QObject):
    def __init__(self, parent, skip_failed=True):
        """
        Sane History
        :param parent: MainWindow
        :param skip_failed: Skip failed entries (remove from history regardless action succeeds or not)
        """
        QObject.__init__(self, parent=parent)
        self.logger = create_logger(__name__)
        self.root = parent
        self.parent = parent
        self.items = []
        self.skip_failed = skip_failed

    def __str__(self):
        """
        Print
        :return:
        """
        if len(self.items) > 0:
            ret_list = []
            for item in self.items:
                ret_list.append(item.__str__())

            return '\n'.join(ret_list)

    def __log__(self):
        """
        Print-to-log
        :return:
        """
        if len(self.items) > 0:
            self.logger.info(self.__str__())

    def log(self):
        """
        Public attribute/interface for print-to-log
        :return:
        """
        self.__log__()

    def add(self, video, action, anti_action):
        """
        Adds Video action to history along with an anti-action to use on an undo()
        :param video: The video object
        :param action: Used for accurate record keeping and possibly future redo()
        :param anti_action: Used for undo()
        :return:
        """
        self.items.append(SaneHistoryItem(self, video, action=action, anti_action=anti_action))
        self.logger.debug("Added History Item: {}".format(self.items[-1]))

    def pop(self, index=-1):
        """
        Pops an HistoryItem, also makes it call delete() on itself ot get picked pu by GC
        :param index: If none given, use last item in list
        :return:
        """
        self.items[index].delete()
        self.items.pop(index)

    def undo(self, index=-1):
        """
        Undoes an action in history, given there exists an anti-action to apply.
        :param index: If none given, use last item in list
        :return:
        """
        if len(self.items) <= 0:
            self.logger.warning("Was told to undo an action when there exists no history!")
            return

        item = self.items[index]
        # Check if the action can be undone
        if item.anti_action:
            try:
                self.logger.info("Undoing action with anti-action '{}' for video: '{}'".format(item.anti_action,
                                                                                               item.video))
                item.anti_action()
                # Undo successful, remove entry from history
            except Exception as exc:
                self.logger.error("Undo FAILED: {}".format(item), exc_info=exc)
                if self.skip_failed:
                    self.logger.info("Skipping failed entry (skip_failed=True)")
                    self.pop(index)
                return

            # If try is successful do the following
            self.pop(index)
            # FIXME: Handle redo / filter anti_action? Former pop pops the anti-action and this one pops the action
            self.pop(index)
        else:
            self.logger.error("Was told to undo an action with no corresponding anti-action: {}".format(item))

