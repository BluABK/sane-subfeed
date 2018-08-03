import runpy

from sane_yt_subfeed.log_handler import create_logger

if __name__ == "__main__":
    logger = create_logger("/__main__")
    logger.info("*** APPLICATION START ***")
    runpy.run_module("sane_yt_subfeed", run_name="__main__")