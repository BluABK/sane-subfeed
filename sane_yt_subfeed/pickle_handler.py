import os

import pickle

OS_PATH = os.path.dirname(__file__)

PICKLE_PATH = os.path.join(OS_PATH, 'resources', 'pickles')

YOUTUBE_PICKLE = os.path.join(PICKLE_PATH, 'youtube_oauth.pkl')


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
    path = os.path.join(PICKLE_PATH, '{}.pkl'.format(key_nr))
    return load_pickle(path)


def load_batch_build_key():
    path = os.path.join(PICKLE_PATH, 'youtube_auth_keys.pkl')
    return load_pickle(path)


def dump_batch_build_key(youtube_list):
    path = os.path.join(PICKLE_PATH, 'youtube_auth_keys.pkl')
    dump_pickle(youtube_list, path)


def dump_build_key(dump_key, key_nr):
    path = os.path.join(PICKLE_PATH, '{}.pkl'.format(key_nr))
    dump_pickle(dump_key, path)


def dump_sub_list(sub_list):
    path = os.path.join(PICKLE_PATH, 'youtube_subs.pkl')
    dump_pickle(sub_list, path)


def load_sub_list():
    path = os.path.join(PICKLE_PATH, 'youtube_subs.pkl')
    return load_pickle(path)

