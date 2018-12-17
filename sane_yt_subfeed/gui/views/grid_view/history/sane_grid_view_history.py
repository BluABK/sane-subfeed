from PyQt5.QtCore import QObject

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.gui.views.grid_view.history.sane_grid_view_history_item import SaneGridViewHistoryItem


class SaneGridViewHistory(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent=parent)
        self.logger = create_logger(__name__)
        self.root = parent.root
        self.parent = parent
        self.items = []

    def __str__(self):
        """
        Print
        :return:
        """
        if len(self.items) > 0:
            '\n'.join(self.items.__str__())

    def __log__(self):
        """
        Print-to-log
        :return:
        """
        if len(self.items) > 0:
            self.logger.info('\n'.join(self.items.__str__()))

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
        self.items.append(SaneGridViewHistoryItem(self.parent, video, action=action, anti_action=anti_action))
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
            except Exception as exc:
                self.logger.error("Undo FAILED: {}".format(item), exc_info=exc)
                return
            # Undo successful, remove entry from history
            self.pop(index)
        else:
            self.logger.warning("Was told to undo an action with no corresponding anti-action: {}".format(item))

