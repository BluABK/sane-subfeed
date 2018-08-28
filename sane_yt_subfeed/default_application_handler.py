import os
import subprocess
import sys

from sane_yt_subfeed import create_logger
from sane_yt_subfeed.config_handler import read_config

OPEN_FILE_HANDLERS_LINUX = ['xdg-open', 'gnome-open']
IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg',]
FAIL_LOG_MSG = "Unable to open default application for '{}' using '{}'"
FAIL_ALL_LOG_MSG = "Unable to open '{}' using default applications, please specify a custom one in config"

logger = create_logger(__name__)


def is_image(file_path):
    for ext in IMAGE_EXTENSIONS: # FIXME: In future use actual MIME type detection not simply *.ext
        if file_path.endswith(ext):
            return True
    return False

# def determine_filetype(file_path):


def open_with_default_application(file_path):
    """
    Determines and launches file with its default application: Image
    :param file_path:
    :return:
    """
    # Determine file type
    if is_image(file_path):
        custom_app = read_config('DefaultApp', 'Image', literal_eval=False)
        print(custom_app)
    else:
        logger.error("No default application extensions specified for {}".format(file_path))
        return
    try:
        if sys.platform.startswith('linux'):
            if custom_app:
                try:
                    subprocess.call(custom_app, file_path)
                except Exception as e:
                    logger.error("{} (custom)".format(FAIL_LOG_MSG.format(file_path, custom_app)), exc_info=e)
                    pass
            else:
                for open_file_handler in OPEN_FILE_HANDLERS_LINUX:
                    try:
                        subprocess.call([open_file_handler, file_path])
                    except Exception as e:
                        logger.debug(FAIL_LOG_MSG.format(file_path, open_file_handler), exc_info=e)
                        pass
                # Reached end of loop, no valid applications
                logger.error(FAIL_ALL_LOG_MSG.format(file_path))

        else:
            # OS = Windows
            if custom_app:
                try:
                    subprocess.Popen([custom_app, file_path])  # os.startfile doesn't really do arguments...
                except Exception as e:
                    logger.error("{} (custom)".format(FAIL_LOG_MSG.format(file_path, custom_app)), exc_info=e)
                    pass
            else:
                os.startfile(file_path)
    except Exception as e_anything:
        logger.exception(e_anything)
        pass
