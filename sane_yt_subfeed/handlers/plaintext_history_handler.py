import datetime

from sane_yt_subfeed.absolute_paths import HISTORY_FILE_PATH
from sane_yt_subfeed.handlers.log_handler import create_logger

logger = create_logger(__name__)


def get_plaintext_history():
    """
    Read the history file and return the entire thing as a string
    :return:
    """
    history_str = None
    try:
        with open(HISTORY_FILE_PATH, encoding='utf-8') as f:
            history_str = f.read()
    except IOError as e_ioerr:
        logger.error("Failed opening history.txt file!", exc_info=e_ioerr)

    return history_str


def update_plaintext_history(entry_str):
    """
    Add an entry to the history file
    :param entry_str:
    :return:
    """
    try:
        with open(HISTORY_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write("[{}] {}\n".format(datetime.datetime.utcnow().isoformat(' '), entry_str))
    except IOError as e_ioerr:
        logger.error("Failed opening history.txt file!", exc_info=e_ioerr)
