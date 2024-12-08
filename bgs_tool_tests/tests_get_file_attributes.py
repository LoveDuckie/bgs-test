"""
Tests: get_file_attributes
"""

import unittest
from typing import List
from unittest.mock import MagicMock, patch

from bgs_tool.__main__ import get_file_attributes
from bgs_tool.types import FileAttributes
from bgs_tool.helpers.helpers_files import (
    create_temp_dir_with_test_files,
)


class TestGetFileAttributes(unittest.TestCase):
    """
    Unit tests for the `get_file_attributes` function.
    """

    @patch("os.scandir")
    @patch("bgs_tool.__main__.os.path.isdir")
    @patch("bgs_tool.__main__.ProcessPoolExecutor")
    @patch("bgs_tool.__main__.as_completed")
    def test_get_file_attributes(
        self,
        mock_as_completed,
        mock_process_pool_executor,
        mock_path_isdir,
        mock_scandir,
    ):
        """
        Test `get_file_attributes` with valid file entries.

        :param mock_scandir: Mock for `os.scandir` to simulate file entries.
        :assert: File attributes are correctly extracted and returned.
        """
        mock_entry_result = MagicMock()
        mock_entry = MagicMock()
        mock_entry.is_file.return_value = True
        mock_entry.name = "test.txt"
        mock_entry.stat.return_value = MagicMock(
            st_size=100, st_mtime=1640995200
        )
        mock_entry.__getitem__.side_effect = lambda key: {
            "name": "test.txt",
            "size_bytes": 100,
        }[key]
        mock_entry_result.result.return_value = mock_entry

        mock_path_isdir.return_value = True

        mock_scandir.return_value.__enter__.return_value = [mock_entry]
        mock_scandir.return_value.__exit__.return_value = None
        mock_process_pool_executor.return_value.__enter__.return_value = (
            MagicMock()
        )
        mock_process_pool_executor.return_value.__exit__.return_value = None
        mock_as_completed.return_value = [mock_entry_result]

        logger = MagicMock()
        attributes = list(get_file_attributes("source", logger))
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes[0]["name"], "test.txt")
        self.assertEqual(attributes[0]["size_bytes"], 100)

    @patch("bgs_tool.__main__.os.path.isdir")
    def test_get_file_attributes_temp_files(self, mock_path_isdir):
        """
        Test `get_file_attributes` with valid file entries.

        :assert: File attributes are correctly extracted and returned.
        """
        mock_path_isdir.return_value = True

        logger = MagicMock()
        source_dir: str | None = None
        with create_temp_dir_with_test_files(min_files=5, max_files=5) as tf:
            source_dir = tf
        attributes: list[FileAttributes] = list(
            get_file_attributes(source_dir, logger)
        )
        self.assertIsInstance(attributes, List)
        self.assertEqual(len(attributes), 5)
        # self.assertEqual(attributes[0]["name"], "test.txt")
        # self.assertEqual(attributes[0]["size_bytes"], 100)
