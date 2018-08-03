from sane_yt_subfeed.log_handler import create_logger
from sane_yt_subfeed.cli import cli

logger = create_logger("__main__")

if __name__ == "__main__":
    logger.info("Launching cli...")
    cli()
