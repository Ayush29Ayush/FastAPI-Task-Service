import sys
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    """
    Default logging handler for intercepting standard logging
    messages and redirecting them to Loguru.
    """
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    """
    Configures the Loguru logger for the application.
    Removes default handlers and adds a new one with a
    structured format. Avoids logging sensitive info.
    """
    # Remove default handler
    logger.remove()

    # Add new handler
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        # Secure logging: sensitive fields must be filtered at call site
        # This format avoids automatically logging request/response bodies.
    )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logger.info("Logging configured successfully.")