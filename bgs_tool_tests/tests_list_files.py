"""
Tests: List Files
"""

import tempfile
import unittest
from unittest.mock import MagicMock, patch

from bgs_tool.__main__ import list_files
from bgs_tool.helpers.helpers_files import create_test_files


class TestListFiles(unittest.TestCase):
    """
    Unit tests for the `list_files` function.
    """

    @patch("os.scandir")
    @patch("bgs_tool.__main__.os.path.isdir")
    def test_list_files_valid(self, mock_isdir, mock_scandir):
        """
        Test `list_files` with a valid directory.

        :assert: The function yields valid file entries.
        """
        mock_entry = MagicMock()
        mock_entry.is_file.return_value = True
        mock_entry.name = "test.txt"
        mock_scandir.return_value.__enter__.return_value = [mock_entry]
        mock_scandir.return_value.__exit__.return_value = None
        mock_isdir.return_value = True

        logger = MagicMock()
        files = list(list_files("source", logger))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "test.txt")

    def list_list_files_test_files(self):
        """
        Test `list_files` with a valid directory.

        :assert: The function yields valid file entries.
        """
        mock_entry = MagicMock()
        mock_entry.is_file.return_value = True
        mock_entry.name = "test.txt"
        # mock_scandir.return_value = [mock_entry]

        logger = MagicMock()
        with tempfile.TemporaryDirectory() as temp_dir:
            create_test_files(path=temp_dir, min_files=5, max_files=5)
            files = list(list_files(temp_dir, logger))
        self.assertEqual(len(files), 5)

    def list_list_files_test_files_randomized(self):
        """
        Test `list_files` with a valid directory.

        :assert: The function yields valid file entries.
        """
        mock_entry = MagicMock()
        mock_entry.is_file.return_value = True
        mock_entry.name = "test.txt"
        # mock_scandir.return_value = [mock_entry]

        min_files = 5
        max_files = 10

        logger = MagicMock()
        with tempfile.TemporaryDirectory() as temp_dir:
            create_test_files(
                path=temp_dir, min_files=min_files, max_files=max_files
            )
            files = list(list_files(temp_dir, logger))
        self.assertGreaterEqual(len(files), min_files)
        self.assertLessEqual(len(files), max_files)
        # self.assertEqual(files[0].name, "test.txt")

    def test_list_files_invalid_directory(self):
        """
        Test `list_files` with an invalid directory.

        :assert: IOError is raised for a non-existent directory.
        """
        logger = MagicMock()
        with self.assertRaises(IOError):
            list(list_files("invalid_dir", logger))
