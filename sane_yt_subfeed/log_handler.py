#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import SocketHandler

from sane_yt_subfeed.handlers.config_handler import read_config

LOG_FILE_HANDLER = None
LOG_FILE = 'debug.log'
# create formatter and add it to the handlers
FORMATTER = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
DEBUG6_LEVEL_NUM = 5
DEBUG7_LEVEL_NUM = 4
DEBUG8_LEVEL_NUM = 3
DEBUG9_LEVEL_NUM = 2
SPAM_LEVEL_NUM = 1

OS_PATH = os.path.dirname(__file__)
LOGDIR = os.path.join(OS_PATH, 'logs')

if read_config('Logging', 'use_socket_log'):
    log_socket_instance = logging.getLogger('r')
    log_level = read_config('Logging', 'log_level')
    log_socket_instance.setLevel(log_level)  # to send all records to socket logger

    port = read_config('Logging', 'logging_port')
    socket_handler = SocketHandler('127.0.0.1', port)  # default listening address
    log_socket_instance.addHandler(socket_handler)

# Add custom logging levels
logging.addLevelName(DEBUG2_LEVEL_NUM, "DEBUG2")
logging.addLevelName(DEBUG3_LEVEL_NUM, "DEBUG3")
logging.addLevelName(DEBUG4_LEVEL_NUM, "DEBUG4")
logging.addLevelName(DEBUG5_LEVEL_NUM, "DEBUG5")
logging.addLevelName(DEBUG6_LEVEL_NUM, "DEBUG6")
logging.addLevelName(DEBUG7_LEVEL_NUM, "DEBUG7")
logging.addLevelName(DEBUG8_LEVEL_NUM, "DEBUG8")
logging.addLevelName(DEBUG9_LEVEL_NUM, "DEBUG9")
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


def debug6(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG6
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG6_LEVEL_NUM):
        self._log(DEBUG6_LEVEL_NUM, message, args, **kws)


def debug7(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG7
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG7_LEVEL_NUM):
        self._log(DEBUG7_LEVEL_NUM, message, args, **kws)


def debug8(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG8
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG8_LEVEL_NUM):
        self._log(DEBUG8_LEVEL_NUM, message, args, **kws)


def debug9(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG9
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG9_LEVEL_NUM):
        self._log(DEBUG9_LEVEL_NUM, message, args, **kws)


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
logging.Logger.debug6 = debug6
logging.Logger.debug7 = debug7
logging.Logger.debug8 = debug8
logging.Logger.debug9 = debug9
logging.Logger.spam = spam


def create_logger_socket(facility):
    """
    Create and return a a logging instance that logs to socket.
    :param facility:
    :return:
    """
    return log_socket_instance.getChild(facility)


def create_file_handler(log_file=LOG_FILE, formatter=FORMATTER):
    """
    Creates *the* (singular) file handler for logging to text file.

    File handler needs to be global and a singular instance,
    to avoid spamming FDs for each create_logger() call.
    :param log_file:
    :param formatter:
    :return:
    """
    global LOG_FILE_HANDLER
    # Only create one instance of the file handler
    if not read_config('Logging', 'use_socket_log') and LOG_FILE_HANDLER is None:
        LOG_FILE_HANDLER = logging.FileHandler(os.path.join(LOGDIR, log_file), encoding="UTF-8")
        LOG_FILE_HANDLER.setLevel(logging.DEBUG)
        LOG_FILE_HANDLER.setFormatter(formatter)


def create_logger_file(facility, formatter=FORMATTER):
    """
    Create and return a a logging instance that logs to file.
    :param facility:
    :param formatter:
    :return:
    """
    global LOG_FILE_HANDLER
    log_file_instance = logging.getLogger(facility)

    log_file_instance.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    if not os.path.exists(LOGDIR):
        os.makedirs(LOGDIR)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # patch the default logging formatter to use unicode format string
    logging._defaultFormatter = logging.Formatter(u"%(message)s")
    ch.setFormatter(formatter)

    # add the handlers to the logger
    log_file_instance.addHandler(LOG_FILE_HANDLER)
    log_file_instance.addHandler(ch)

    return log_file_instance


def create_logger(facility):
    """
    Creates a logger function based on the logging library
    :param facility:     Name of what's calling logger.
    :return:
    """
    create_file_handler()
    # create logger
    if read_config('Logging', 'use_socket_log'):
        return create_logger_socket(facility)
    else:
        return create_logger_file(facility)


# Default logger facility
logger = create_logger('sane-subfeed')
