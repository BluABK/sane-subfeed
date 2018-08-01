import os
import timeit


def get_yt_file(search_path, id):
    for root, dirs, files in os.walk(search_path):
        for name in files:
            if id in name:
                return name
    return None
