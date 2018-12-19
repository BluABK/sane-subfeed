#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import SocketHandler

from sane_yt_subfeed.config_handler import read_config

"""
Default Logging levels
CRITICAL 	50
ERROR 	    40
WARNING 	30
INFO 	    20
DEBUG 	    10
NOTSET 	    0
"""

"""
Custom Logging levels
"""
DEBUG2_LEVEL_NUM = 9
DEBUG3_LEVEL_NUM = 8
DEBUG4_LEVEL_NUM = 7
DEBUG5_LEVEL_NUM = 6
SPAM_LEVEL_NUM = 5

OS_PATH = os.path.dirname(__file__)
LOGDIR = os.path.join(OS_PATH, 'logs')

if read_config('Logging', 'use_socket_log'):
    log = logging.getLogger('r')
    log_level = read_config('Logging', 'log_level')
    log.setLevel(log_level)  # to send all records to cutelog

    port = read_config('Logging', 'logging_port')
    socket_handler = SocketHandler('127.0.0.1', port)  # default listening address
    log.addHandler(socket_handler)

# Add custom logging levels
logging.addLevelName(DEBUG2_LEVEL_NUM, "DEBUG2")
logging.addLevelName(DEBUG3_LEVEL_NUM, "DEBUG3")
logging.addLevelName(DEBUG4_LEVEL_NUM, "DEBUG4")
logging.addLevelName(DEBUG5_LEVEL_NUM, "DEBUG5")
logging.addLevelName(SPAM_LEVEL_NUM, "SPAM")


def debug2(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG2
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG2_LEVEL_NUM):
        self._log(DEBUG2_LEVEL_NUM, message, args, **kws)


def debug3(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG3
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG3_LEVEL_NUM):
        self._log(DEBUG3_LEVEL_NUM, message, args, **kws)


def debug4(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG4
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG4_LEVEL_NUM):
        self._log(DEBUG4_LEVEL_NUM, message, args, **kws)


def debug5(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG5
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG5_LEVEL_NUM):
        self._log(DEBUG5_LEVEL_NUM, message, args, **kws)


def spam(self, message, *args, **kws):
    """
    Custom Logging level log function: SPAM

    The logging level that is used for really spamming debug logging

    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(SPAM_LEVEL_NUM):
        self._log(SPAM_LEVEL_NUM, message, args, **kws)


# Define logging attributes for log levels and assign them to the appropriate function
logging.Logger.debug2 = debug2
logging.Logger.debug3 = debug3
logging.Logger.debug4 = debug4
logging.Logger.debug5 = debug5
logging.Logger.spam = spam


def create_logger(facility, logfile='debug.log'):
    """
    Creates a logger function based on the logging library
    :param facility:    Name of what's calling logger.
    :param logfile:     File to log to (default: 'debug.log')
    :return:
    """
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
