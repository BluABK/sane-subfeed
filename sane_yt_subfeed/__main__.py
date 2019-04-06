from sane_yt_subfeed.run import cli
from sane_yt_subfeed.handlers.log_handler import create_logger

logger = create_logger(__name__)

if __name__ == "__main__":
    logger.info("Launching cli...")
    cli()
