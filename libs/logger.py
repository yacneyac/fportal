# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

import logging.handlers
import tornado.log

from libs.conf import ACCESS_PATH, APP_PATH, GEN_PATH, LOG_LVL

# todo: add to formatter user's login or ID

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                              datefmt='%d-%m-%Y %H:%M:%S')


ac = tornado.log.access_log
hdlr = logging.handlers.TimedRotatingFileHandler(ACCESS_PATH, when="midnight", backupCount=5)
hdlr.setFormatter(formatter)
ac.addHandler(hdlr)

gen = tornado.log.gen_log
hdlr = logging.handlers.TimedRotatingFileHandler(GEN_PATH, when="midnight", backupCount=5)
hdlr.setFormatter(formatter)
gen.addHandler(hdlr)


log = tornado.log.app_log
hdlr = logging.handlers.TimedRotatingFileHandler(APP_PATH, when="midnight", backupCount=5)
hdlr.setFormatter(formatter)
log.setLevel(LOG_LVL)
log.addHandler(hdlr)
