## Log Trimmer

I let my fermenter run for several months and the log files filled (and corrupted) my SD card.  This add-on prevents this.

1. Replaces file handler on primary (app.log) logger with TimedRotatingFileHandler.  7 daily logs are kept.

2. Checks sensor/kettle/fermenter/etc logs once every hour.  If length exceeds system parameter 'max_log_lines', log will be trimmed to 90% of max, preserving most-recent data.

3. Removes duplicate temperature entries to decrease chart load times.
