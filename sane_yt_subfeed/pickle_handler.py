import os
import pickle
import time

from sane_yt_subfeed.log_handler import logger

OS_PATH = os.path.dirname(__file__)

PICKLE_PATH = os.path.join(OS_PATH, 'resources', 'pickles')

YOUTUBE_PICKLE = os.path.join(PICKLE_PATH, 'youtube_oauth.pkl')


def dump_youtube(youtube):
    logger.info("Dumping youtube pickle")
    dump_pickle(youtube, YOUTUBE_PICKLE)


def dump_pickle(pickle_object, path):
    logger.info("Dumping pickle obj {} to {}".format(pickle_object, path))
    with open(path, 'wb') as pickle_output:
        pickle.dump(pickle_object, pickle_output, pickle.HIGHEST_PROTOCOL)


def load_pickle(path):
    logger.info("Loading pickle from {}".format(path))
    tries = 1
    while tries <= 6:
        try:
            with open(path, 'rb') as pickle_input:
                pickle_object = pickle.load(pickle_input)
            return pickle_object
        except MemoryError as mem_exc:
            logger.error("Loading attempt #{} of pickle failed, retrying {} more time(s)...".format(tries, 5-tries))
            logger.exception(mem_exc)
            if tries >= 6:
                tries += 1
                time.sleep(1)
                continue
            else:
                logger.fatal("Loading of pickle has utterly failed, terminating application!")
                raise mem_exc


def load_youtube():
    logger.info("Loading YouTube pickle")
    return load_pickle(YOUTUBE_PICKLE)


def load_build_key(key_nr):
    path = os.path.join(PICKLE_PATH, '{}.pkl'.format(key_nr))
    logger.info("Loading buildkey {} pickle from {}".format(key_nr, path))
    return load_pickle(path)


def load_batch_build_key():
    path = os.path.join(PICKLE_PATH, 'youtube_auth_keys.pkl')
    logger.info("Batch-Loading buildkey pickle from {}".format(path))
    return load_pickle(path)


def dump_batch_build_key(youtube_list):
    path = os.path.join(PICKLE_PATH, 'youtube_auth_keys.pkl')
    logger.info("Batch-Dumping buildkey pickle to {}".format(path))
    dump_pickle(youtube_list, path)


def dump_build_key(dump_key, key_nr):
    path = os.path.join(PICKLE_PATH, '{}.pkl'.format(key_nr))
    logger.info("Dumping buildkey pickle to {}".format(path))
    dump_pickle(dump_key, path)


def dump_sub_list(sub_list):
    path = os.path.join(PICKLE_PATH, 'youtube_subs.pkl')
    logger.info("Dumping sublist pickle to {}".format(path))
    dump_pickle(sub_list, path)


def load_sub_list():
    path = os.path.join(PICKLE_PATH, 'youtube_subs.pkl')
    logger.info("Loading sublist pickle from {}".format(path))
    return load_pickle(path)

