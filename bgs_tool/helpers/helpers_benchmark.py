"""
Helper functions for benchmarking
"""

import logging
import time
import functools

from bgs_tool.helpers.helpers_logging import get_logger


def benchmark(func, *, logger: logging.Logger | None = None):
    """
    Benchmark a function. Subtract the time it finished, from the time that it started to get the delta
    :param func:
    :param logger: The logger instance
    :return:
    """
    logger = get_logger() if logger is None else logger

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logger.debug(
            f"{func.__name__} executed in {end_time - start_time:.6f} seconds"
        )
        return result

    return wrapper
