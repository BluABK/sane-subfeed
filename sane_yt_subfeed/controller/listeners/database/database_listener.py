import time

# from PySide2.QtCore import QObject, SIGNAL, SLOT
from PySide2.QtCore import QObject, Signal, Slot

from sane_yt_subfeed import create_logger


class DatabaseListener(QObject):
    static_instance = None

    databaseUpdated = Signal(int)
    refreshVideos = Signal(str)

    # Signal is a thread ID
    startWrite = Signal(str)
    finishWrite = Signal(str)
    startRead = Signal(str)
    finishRead = Signal(str)

    dbStateChanged = Signal(int)

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
        self.logger.db_debug("Currently {} writing threads and {} reading threads".format(len(self.writing_threads),
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
        self.logger.db_debug("Updated db state to {}".format(self.db_state))
        self.dbStateChanged.emit(self.db_state)

    """
    Shibroken (not a typo) workaround (bug: https://bugreports.qt.io/browse/PYSIDE-648):
    
    When int > 4 byte, send it as a string and then convert it back to int on this end. 
    """

    def start_write(self, db_id):
        """
        Appends the DB write thread id to a a list of threads and logs it.
        :param db_id:
        :return:
        """
        try:
            self.writing_threads.append(int(db_id))
            self.update_db_stat()
            self.logger.db_debug("Added db_id {} to writing_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to add {} to writing_threads - {}".format(db_id, e), exc_info=1)

    def finish_write(self, db_id):
        """
        Removes the DB write thread id to a a list of threads and logs it.
        :param db_id:
        :return:
        """
        try:
            self.writing_threads.remove(int(db_id))
            self.update_db_stat()
            self.logger.db_debug("Removed db_id {} from writing_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to remove {} from writing threads - {}".format(db_id, e), exc_info=1)

    def start_read(self, db_id):
        """
        Appends the DB read thread id to a a list of threads and logs it.
        :param db_id:
        :return:
        """
        try:
            self.reading_threads.append(int(db_id))
            self.update_db_stat()
            self.logger.db_debug("Added db_id {} to reading_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to add {} to reading_threads - {}".format(db_id, e), exc_info=1)

    def finish_read(self, db_id):
        """
        Removes the DB read thread id to a a list of threads and logs it.
        :param db_id:
        :return:
        """
        try:
            self.reading_threads.remove(int(db_id))
            self.update_db_stat()
            self.logger.db_debug("Removed db_id {} from reading_threads".format(db_id))
        except Exception as e:
            self.logger.warning("Failed to remove {} from reading_threads - {}".format(db_id, e), exc_info=1)

    def run(self):
        while True:
            time.sleep(2)

    @Slot()
    def refresh_videos(self):
        self.logger.info('Reloading videos')
