"""
Tests: Group Files
"""

import unittest
from typing import Iterable
from unittest.mock import MagicMock

from bgs_tool import BYTES_IN_MB
from bgs_tool.__main__ import group_files_compact, group_files
from bgs_tool.types import FileAttributes


class TestGroupFiles(unittest.TestCase):
    """
    Unit tests for the `group_files` function.
    """

    def test_group_files_compact_valid(self):
        """
        Test `group_files_compact` with files that fit within the group size.

        :assert: Files are grouped correctly according to the size limit.
        """
        files: Iterable[FileAttributes] = [
            {
                "name": "file1",
                "size_bytes": 5 * BYTES_IN_MB,
                "last_modified": "2024-12-03T12:00:00",
            },
            {
                "name": "file2",
                "size_bytes": 3 * BYTES_IN_MB,
                "last_modified": "2024-12-03T12:00:00",
            },
        ]
        logger = MagicMock()
        groups = group_files_compact(files, 10 * BYTES_IN_MB, logger)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 2)

    def test_group_files_valid(self):
        """
        Test `group_files` with files that fit within the group size.

        :assert: Files are grouped correctly according to the size limit.
        """
        files: Iterable[FileAttributes] = [
            {
                "name": "file1",
                "size_bytes": 5 * BYTES_IN_MB,
                "last_modified": "2024-12-03T12:00:00",
            },
            {
                "name": "file2",
                "size_bytes": 3 * BYTES_IN_MB,
                "last_modified": "2024-12-03T12:00:00",
            },
        ]
        logger = MagicMock()
        groups = group_files(files, 10 * BYTES_IN_MB, logger)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 2)
