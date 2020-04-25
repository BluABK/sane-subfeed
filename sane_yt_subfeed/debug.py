from sane_yt_subfeed.handlers.log_handler import create_logger

logger = create_logger("DEBUG STUFF")

date_formats = {}


def add_date_format(date_fmt):
    global date_formats
    if date_fmt in date_formats:
        date_formats[date_fmt] += 1
    else:
        date_formats[date_fmt] = 1


def clear_date_formats():
    global date_formats
    date_formats = {}


def summary():
    logger.debug5("sane_yt_subfeed.debug.date_formats:")
    logger.debug5(date_formats)
