import os
import datetime

from sane_yt_subfeed.log_handler import create_logger

OS_PATH = os.path.dirname(__file__)
LOGDIR = os.path.join(OS_PATH, 'logs')
HISTORY_FILENAME = 'history.txt'
HISTORY_FILEPATH = os.path.join(LOGDIR, HISTORY_FILENAME)

logger = create_logger(__name__)


def get_history():
    """
    Read the history file and return the entire thing as a string
    :return:
    """
    history_str = None
    try:
        with open(HISTORY_FILEPATH, encoding='utf-8') as f:
            history_str = f.read()
    except IOError as e_ioerr:
        logger.error("Failed opening history.txt file!", exc_info=e_ioerr)

    return history_str


def update_history(entry_str):
    """
    Add an entry to the history file
    :param entry_str:
    :return:
    """
    try:
        with open(HISTORY_FILEPATH, 'a', encoding='utf-8') as f:
            f.write("[{}] {}\n".format(datetime.datetime.utcnow().isoformat(' '), entry_str))
    except IOError as e_ioerr:
        logger.error("Failed opening history.txt file!", exc_info=e_ioerr)
