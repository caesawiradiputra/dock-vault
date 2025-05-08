import sys

from loguru import logger

from configs.config import LOG_PATH


def configure_logger():
    """Configure Loguru logger"""
    # Remove default handler
    logger.remove()

    # Add file rotation handler
    logger.add(
        LOG_PATH / "credential_manager.log",
        rotation="1 MB",
        retention="30 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True,  # Thread-safe logging
    )

    # Add console handler
    logger.add(
        sys.stderr,
        level="DEBUG",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # Configure to catch all exceptions
    logger.catch(reraise=False)
