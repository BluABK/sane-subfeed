#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import subprocess
from logging.handlers import SocketHandler

from sane_yt_subfeed.config_handler import read_config

"""
Logging levels
CRITICAL 	50
ERROR 	    40
WARNING 	30
INFO 	    20
DEBUG 	    10
NOTSET 	    0
"""

OS_PATH = os.path.dirname(__file__)
LOGDIR = os.path.join(OS_PATH, 'logs')
if read_config('Logging', 'use_socket_log'):
    log = logging.getLogger('r')
    log_level = read_config('Logging', 'log_level')
    log.setLevel(log_level)  # to send all records to cutelog

    port = read_config('Logging', 'logging_port')
    socket_handler = SocketHandler('127.0.0.1', port)  # default listening address
    log.addHandler(socket_handler)

SPAM_LEVEL_NUM = 5
logging.addLevelName(SPAM_LEVEL_NUM, "SPAM")


def spam(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(SPAM_LEVEL_NUM):
        self._log(SPAM_LEVEL_NUM, message, args, **kws)


logging.Logger.spam = spam


def create_logger(facility, logfile='debug.log'):
    # create logger
    if read_config('Logging', 'use_socket_log'):
        return log.getChild(facility)
    else:
        log_instance = logging.getLogger(facility)

        log_instance.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        if not os.path.exists(LOGDIR):
            os.makedirs(LOGDIR)
        fh = logging.FileHandler(os.path.join(LOGDIR, logfile), encoding="UTF-8")
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # patch the default logging formatter to use unicode format string
        logging._defaultFormatter = logging.Formatter(u"%(message)s")
        # create formatter and add it to the handlers
        formatter = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        log_instance.addHandler(fh)
        log_instance.addHandler(ch)

        return log_instance


# Default logger facility
logger = create_logger('sane-subfeed')
