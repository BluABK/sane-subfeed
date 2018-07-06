import os

import pickle

OS_PATH = os.path.dirname(__file__)

YOUTUBE_PICKLE = os.path.join(OS_PATH, 'resources', 'youtube.pkl')


def dump_youtube(youtube):
    dump_pickle(youtube, YOUTUBE_PICKLE)


def dump_pickle(pickle_object, path):
    with open(path, 'wb') as pickle_output:
        pickle.dump(pickle_object, pickle_output, pickle.HIGHEST_PROTOCOL)


def load_pickle(path):
    with open(path, 'rb') as pickle_input:
        pickle_object = pickle.load(pickle_input)
    return pickle_object


def load_youtube():
    return load_pickle(YOUTUBE_PICKLE)


def load_build_key(key_nr):
    path = os.path.join(OS_PATH, 'resources', 'dump_keys', '{}.pkl'.format(key_nr))
    return load_pickle(path)


def dump_build_key(dump_key, key_nr):
    path = os.path.join(OS_PATH, 'resources', 'dump_keys', '{}.pkl'.format(key_nr))
    dump_pickle(dump_key, path)
