# -*- coding: utf-8 -*-
################################################################################

from modules import cbpi
from os import system, rename
from glob import glob
import logging, logging.handlers

################################################################################
# Globals
################################################################################
RUN_INTERVAL = 3600

MAX_LOG_LINES = 0
TRIM_LOG_LINES = 0
DEFAULT_LOG_LINES = 100000

LOG_DIR = "./logs/"
APP_LOG = LOG_DIR + "app.log"
TMP_LOG = LOG_DIR + "tmplog"

# from modules/app_config.py
LOG_FORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'

################################################################################
# Methods
################################################################################
def update_max_log_globals():
    global MAX_LOG_LINES, TRIM_LOG_LINES
    value = int(cbpi.get_config_parameter("max_log_lines", 0))
    if MAX_LOG_LINES != value:
        MAX_LOG_LINES = value
        TRIM_LOG_LINES = MAX_LOG_LINES * 9 / 10
        cbpi.app.logger.info("LogLimiter: max_log_lines set to {}".format(MAX_LOG_LINES))

#-------------------------------------------------------------------------------
@cbpi.initalizer(order=100)
def init(cbpi):
    cbpi.app.logger.info("LogLimiter: initialize")

    # setup max lines parameter for sensor etc logs
    param = cbpi.get_config_parameter("max_log_lines", None)
    if param is None:
        cbpi.app.logger.info("LogLimiter: create system parameter")
        try:
            cbpi.add_config_parameter("max_log_lines", DEFAULT_LOG_LINES, "number", "Max Log Lines")
        except Exception as e:
            cbpi.app.logger.error("LogLimiter: {}".format(e))
    update_max_log_globals()

    # replace default file handler with rotating handler for main app.log
    try:
        new_file_handler = logging.handlers.TimedRotatingFileHandler(APP_LOG, when='midnight', interval=1, backupCount=7)
        new_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger = logging.getLogger()
        for one_handler in root_logger.handlers:
            if isinstance(one_handler, logging.FileHandler):
                root_logger.removeHandler(one_handler)
        root_logger.addHandler(new_file_handler)
        cbpi.app.logger.info("LogLimiter: logger file handler replaced")
    except Exception as e:
        cbpi.app.logger.error("LogLimiter: {}".format(e))


#-------------------------------------------------------------------------------
@cbpi.backgroundtask(key="trim_value_logs", interval=RUN_INTERVAL)
def trim_value_logs(api):
    update_max_log_globals()

    if MAX_LOG_LINES: # skip if zero
        cbpi.app.logger.info("LogLimiter: checking log files")

        log_files = glob(LOG_DIR + "*.log")
        try: log_files.remove(APP_LOG)
        except: pass

        for log_file in log_files:
            log_lines = sum(1 for line in open(log_file))
            if log_lines > MAX_LOG_LINES:
                cbpi.app.logger.info("LogLimiter: trimming {} from {} to {} lines".format(log_file, log_lines, TRIM_LOG_LINES))
                system("tail -n {} {} > {}".format(TRIM_LOG_LINES, log_file, TMP_LOG))
                rename(TMP_LOG, log_file)
