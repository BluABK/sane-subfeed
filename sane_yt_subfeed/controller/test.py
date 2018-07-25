import time

from PyQt5.QtCore import QObject, pyqtSignal


class MainWindowListener(QObject):
    refreshVideosfwheiuf = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideosfwheiuf.connect(self.refresh_videoswesfsef)

    def run(self):
        while True:
            time.sleep(2)

    def refresh_videoswesfsef(self):
        print('refresh')


if __name__ == '__main__':
    subscriptions_len = 217
    quota = 30*1000
    max_search_quota = int(0.9*quota)

    search_mod = divmod(max_search_quota, subscriptions_len*100)

    search_pages = search_mod[0]
    list_pages = int((quota-max_search_quota+search_mod[1])/(subscriptions_len*3))
    print(list_pages)
    print(search_pages)
