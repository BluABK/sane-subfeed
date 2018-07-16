#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

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

# create logger with 'spam_application'
logger = logging.getLogger('debug')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)
fh = logging.FileHandler(os.path.join(LOGDIR, 'debug.log'), encoding="UTF-8")
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
logger.addHandler(fh)
logger.addHandler(ch)

# logger.info('creating an instance of auxiliary_module.Auxiliary')
# a = auxiliary_module.Auxiliary()
# logger.info('created an instance of auxiliary_module.Auxiliary')
# logger.info('calling auxiliary_module.Auxiliary.do_something')
# a.do_something()
# logger.info('finished auxiliary_module.Auxiliary.do_something')
# logger.info('calling auxiliary_module.some_function()')
# auxiliary_module.some_function()
# logger.info('done with auxiliary_module.some_function()')