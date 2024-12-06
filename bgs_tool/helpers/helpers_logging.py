"""
Helper functions for logging
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from bgs_tool import __title__, BYTES_IN_MB

_logger: logging.Logger | None = None


def _get_default_log_filename() -> str:
    """
    Generate the default log file name.
    :return:
    """
    return __title__ + "_" + datetime.now().strftime("%Y_%m_%d") + ".log"


def get_default_log_filepath() -> str:
    """
    Generate the absolute path to the default log file.
    :return:
    """
    return os.path.join(os.getcwd(), _get_default_log_filename())


def get_logger(
    name: str = __title__,
    *,
    filepath: str = get_default_log_filepath(),
    force_create: bool = False,
    verbosity: int = logging.DEBUG,
) -> logging.Logger:
    """
    Get the logger instance
    :param verbosity: The verbosity of the logger.
    :param filepath: The absolute path to the log file.
    :param force_create: Force the instantiation of a new logger instance.
    :param name: The name of the logger.
    :return:
    """
    global _logger

    if not _logger or force_create:
        if not filepath:
            raise ValueError("The log filepath is invalid or null")
        _logger = _create_logger(name, filepath=filepath, verbosity=verbosity)

    return _logger


def _create_logger(
    name: str = __title__,
    *,
    filepath: str = get_default_log_filepath(),
    verbosity: int = logging.DEBUG,
) -> logging.Logger:
    """
    Create a logger instance
    :param name: The name of the logger.
    :param filepath: The absolute path to the log file.
    :param verbosity: The verbosity of the logger.
    :return:
    """
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(verbosity)

    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    stream_handler: logging.StreamHandler = logging.StreamHandler()
    stream_handler.setLevel(verbosity)
    stream_handler.setFormatter(formatter)

    # Rotate every 5 megabytes.
    file_handler: RotatingFileHandler = RotatingFileHandler(
        filepath, maxBytes=5 * BYTES_IN_MB, backupCount=5
    )
    file_handler.setLevel(verbosity)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
