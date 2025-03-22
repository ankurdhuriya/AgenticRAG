import logging
import sys
from logging.handlers import RotatingFileHandler
from app.config.settings import Settings

settings = Settings()

def configure_logging():
    """
    Configure logging for the application.
    """
    # Set log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Create formatters
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]"
    )

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    # Rotating file handler to limit log file size
    file_handler = RotatingFileHandler(
        "app.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10 MB per file, keep 5 backups
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log a message to confirm logging is configured
    logger.info("Logging configured successfully.")

    return logger