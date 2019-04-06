import time

import pickle

from sane_yt_subfeed.absolute_paths import YOUTUBE_RESOURCE_OAUTH_PICKLE, YOUTUBE_RESOURCE_KEYS_PICKLE
from sane_yt_subfeed.handlers.log_handler import create_logger

logger = create_logger(__name__)


def save_youtube_resource_oauth(youtube):
    """
    Saves the Pickled YouTube OAuth Authenticated Resource object to a .pkl file.
    :param youtube:
    :return:
    """
    logger.info("Dumping youtube pickle")
    dump_pickle(youtube, YOUTUBE_RESOURCE_OAUTH_PICKLE)


def dump_pickle(pickle_object, path):
    """
    Dumps a Pickle object to a .pkl file.
    :param pickle_object:
    :param path:
    :return:
    """
    logger.info("Dumping pickle obj {} to {}".format(pickle_object, path))
    with open(path, 'wb') as pickle_output:
        pickle.dump(pickle_object, pickle_output, pickle.HIGHEST_PROTOCOL)


def load_pickle(path, max_attempts=6):
    """
    Loads a pickle file from path.
    :param path:
    :param max_attempts:
    :return:
    """
    logger.info("Loading pickle from {}".format(path))
    attempt = 1
    while attempt <= max_attempts:
        try:
            with open(path, 'rb') as pickle_input:
                pickle_object = pickle.load(pickle_input)
            return pickle_object
        except MemoryError as mem_exc:
            logger.error("Loading attempt #{} of pickle failed, retrying {} more time(s)...".format(
                attempt, max_attempts - attempt))
            logger.exception("load_pickle exception: ", exc_info=mem_exc)
            logger.debug("pickle path: {}".format(path))
            if attempt <= 6:
                attempt += 1
                time.sleep(1)
                continue
            else:
                logger.fatal("Loading of pickle has utterly failed, terminating application!")
                exit(-3)


def load_youtube_resource_oauth():
    """
    Loads a Pickled YouTube OAuth Authenticated Resource object from file.
    :return:
    """
    logger.info("Loading YouTube OAuth Authenticated Resource object pickle from {}".format(
        YOUTUBE_RESOURCE_OAUTH_PICKLE))
    return load_pickle(YOUTUBE_RESOURCE_OAUTH_PICKLE)


def load_youtube_resource_keys():
    """
    Loads Pickled YouTube API-Key Authenticated Resource objects from file.
    :return:
    """
    logger.info("Loading YouTube API-Key Authenticated Resource objects pickle from {}".format(
        YOUTUBE_RESOURCE_KEYS_PICKLE))
    return load_pickle(YOUTUBE_RESOURCE_KEYS_PICKLE)


def save_youtube_resource_keys(youtube_list):
    """
    Saves Pickled YouTube API-Key Authenticated Resource objects to file.
    :param youtube_list:
    :return:
    """
    logger.info("Saving YouTube API-Key Authenticated Resource objects pickle to {}".format(
        YOUTUBE_RESOURCE_KEYS_PICKLE))
    dump_pickle(youtube_list, YOUTUBE_RESOURCE_KEYS_PICKLE)
