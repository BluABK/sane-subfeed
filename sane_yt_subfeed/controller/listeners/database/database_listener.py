import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from sane_yt_subfeed import create_logger


class DatabaseListener(QObject):
    static_instance = None

    databaseUpdated = pyqtSignal()
    refreshVideos = pyqtSignal()
    startWrite = pyqtSignal(int)
    finishWrite = pyqtSignal(int)
    startRead = pyqtSignal(int)
    finishRead = pyqtSignal(int)
    dbStateChanged = pyqtSignal(int)

    DB_STATE_IDLE = 0
    DB_STATE_READ = 1
    DB_STATE_WRITE = 2
    DB_STATE_READ_WRITE = 3

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.refreshVideos.connect(self.refresh_videos)
        self.logger = create_logger(__name__ + '.DatabaseListener')

        self.reading_threads = []
        self.writing_threads = []

        self.db_state = self.DB_STATE_IDLE

        self.startWrite.connect(self.start_write)
        self.finishWrite.connect(self.finish_write)

        self.startRead.connect(self.start_read)
        self.finishRead.connect(self.finish_read)

        DatabaseListener.static_instance = self

    def update_db_stat(self):
        self.logger.debug7("Currently {} writing threads and {} reading threads".format(len(self.writing_threads),
                                                                                        len(self.reading_threads)))
        if len(self.reading_threads) > 0 and len(self.writing_threads) > 0:
            if self.db_state == self.DB_STATE_READ_WRITE:
                return
            else:
                self.db_state = self.DB_STATE_READ_WRITE
        elif len(self.reading_threads) > 0:
            if self.db_state == self.DB_STATE_READ:
                return
            else:
                self.db_state = self.DB_STATE_READ
        elif len(self.writing_threads) > 0:
            if self.db_state == self.DB_STATE_WRITE:
                return
            else:
                self.db_state = self.DB_STATE_WRITE
        else:
            if self.db_state == self.DB_STATE_IDLE:
                return
            else:
                self.db_state = self.DB_STATE_IDLE
        self.logger.debug7("Updated db state to {}".format(self.db_state))
        self.dbStateChanged.emit(self.db_state)

    def start_write(self, db_id):
        try:
            self.writing_threads.append(db_id)
            self.update_db_stat()
            self.logger.debug7("Added db_id {} to writing_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to add {} to writing_threads - {}".format(db_id, e), exc_info=1)

    def finish_write(self, db_id):
        try:
            self.writing_threads.remove(db_id)
            self.update_db_stat()
            self.logger.debug7("Removed db_id {} from writing_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to remove {} from writing threads - {}".format(db_id, e), exc_info=1)

    def start_read(self, db_id):
        try:
            self.reading_threads.append(db_id)
            self.update_db_stat()
            self.logger.debug7("Added db_id {} to reading_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to add {} to reading_threads - {}".format(db_id, e), exc_info=1)

    def finish_read(self, db_id):
        try:
            self.reading_threads.remove(db_id)
            self.update_db_stat()
            self.logger.debug7("Removed db_id {} from reading_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to remove {} from reading_threads - {}".format(db_id, e), exc_info=1)

    def run(self):
        while True:
            time.sleep(2)

    @pyqtSlot()
    def refresh_videos(self):
        self.logger.info('Reloading videos')
