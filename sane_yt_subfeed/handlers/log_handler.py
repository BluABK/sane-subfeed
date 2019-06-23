#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import SocketHandler

from sane_yt_subfeed.absolute_paths import LOG_DIR
from sane_yt_subfeed.handlers.config_handler import read_config

LOG_FILE_HANDLER = None
LOG_FILE = 'debug.log'
# create formatter and add it to the handlers
FORMATTER = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DEFAULT_LOG_LEVELS = [0, 10, 20, 30, 40, 50]

# Logging levels (practically) static dict.
LOG_LEVELS = {'NOT SET': 0,
              'SPAM': 1,
              'DEBUG9': 2,
              'DEBUG8': 3,
              'DB_DEBUG': 4,
              'DEBUG6': 5,
              'DEBUG5': 6,
              'DEBUG4': 7,
              'DEBUG3': 8,
              'DEBUG2': 9,
              'DEBUG': 10,
              'INFO': 20,
              'DB_INFO': 26,
              'WARNING': 30,
              'ERROR': 40,
              'CRITICAL': 50}


def db_info(self, message, *args, **kws):
    """
    Custom Logging level log function: DB_INFO (Level 26)
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(LOG_LEVELS['DB_INFO']):
        self._log(LOG_LEVELS['DB_INFO'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['DEBUG2']):
        self._log(LOG_LEVELS['DEBUG2'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['DEBUG3']):
        self._log(LOG_LEVELS['DEBUG3'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['DEBUG4']):
        self._log(LOG_LEVELS['DEBUG4'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['DEBUG5']):
        self._log(LOG_LEVELS['DEBUG5'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['DEBUG6']):
        self._log(LOG_LEVELS['DEBUG6'], message, args, **kws)


def db_debug(self, message, *args, **kws):
    """
    Custom Logging level log function: DEBUG7
    :param self:
    :param message: String to log
    :param args: logging args
    :param kws: logging keywords
    :return:
    """
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(LOG_LEVELS['DB_DEBUG']):
        self._log(LOG_LEVELS['DB_DEBUG'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['DEBUG8']):
        self._log(LOG_LEVELS['DEBUG8'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['DEBUG9']):
        self._log(LOG_LEVELS['DEBUG9'], message, args, **kws)


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
    if self.isEnabledFor(LOG_LEVELS['SPAM']):
        self._log(LOG_LEVELS['SPAM'], message, args, **kws)


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
        logfile_path = os.path.join(LOG_DIR, log_file)

        # Make sure logs dir exists, if not create it.
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR)

        # Make sure logfile exists, if not create it.
        if not os.path.isfile(logfile_path):
            open(logfile_path, 'a').close()

        LOG_FILE_HANDLER = logging.FileHandler(logfile_path, encoding="UTF-8")
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
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

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
        logger_instance = create_logger_socket(facility)
    else:
        logger_instance = create_logger_file(facility)

    # Attach a handle to the log levels dict.
    setattr(logger_instance, "my_log_levels", LOG_LEVELS)

    return logger_instance


if read_config('Logging', 'use_socket_log'):
    log_socket_instance = logging.getLogger('r')
    log_level = read_config('Logging', 'log_level')
    log_socket_instance.setLevel(log_level)  # to send all records to socket logger

    port = read_config('Logging', 'logging_port')
    socket_handler = SocketHandler('127.0.0.1', port)  # default listening address
    log_socket_instance.addHandler(socket_handler)

# Add custom logging levels (descending order)
for level, value in LOG_LEVELS.items():
    if value in DEFAULT_LOG_LEVELS:
        # Skip default levels
        continue

    # Add level name and value to static logging instance.
    logging.addLevelName(value, level)

# Define logging attributes for log levels and assign them to the appropriate function
logging.Logger.db_info = db_info
logging.Logger.debug2 = debug2
logging.Logger.debug3 = debug3
logging.Logger.debug4 = debug4
logging.Logger.debug5 = debug5
logging.Logger.debug6 = debug6
logging.Logger.db_debug = db_debug
logging.Logger.debug8 = debug8
logging.Logger.debug9 = debug9
logging.Logger.spam = spam

# Default logger facility
logger = create_logger('sane-subfeed')
