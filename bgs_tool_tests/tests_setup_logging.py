import unittest
from logging import Logger

from bgs_tool.helpers.helpers_logging import get_logger


class TestSetupLogging(unittest.TestCase):
    """
    Unit tests for the `setup_logging` function.
    """

    def test_logger_setup(self):
        """
        Test that `setup_logging` returns a properly
        configured Logger instance.

        :assert: The logger is an instance of `Logger`
        and has handlers attached.
        """
        logger = get_logger()
        self.assertIsInstance(logger, Logger)
        self.assertTrue(logger.hasHandlers())
