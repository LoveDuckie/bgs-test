"""
Unit tests for the application.
"""

import os
import unittest
from unittest.mock import patch, MagicMock, mock_open

from bgs_tool.__main__ import (
    save_groups,
)


class TestSaveGroups(unittest.TestCase):
    """
    Unit tests for the `save_groups` function.
    """

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_groups(self, mock_file, mock_makedirs):
        """
        Test `save_groups` with valid group data.

        :param mock_file: Mock for `open` to simulate file writing.
        :param mock_makedirs: Mock for `os.makedirs` to
        simulate directory creation.
        :assert: JSON files are written correctly for each group.
        """
        groups = [
            [
                {
                    "name": "file1",
                    "size_bytes": 5 * 1024 * 1024,
                    "last_modified": "2024-12-03T12:00:00",
                }
            ],
        ]
        logger = MagicMock()
        save_groups(groups, "output", logger)
        mock_file.assert_called_once_with(
            os.path.join("output", "group_001.json"), "w", encoding="utf-8"
        )
        mock_makedirs.assert_called_once_with("output", exist_ok=True)

    def test_save_groups_no_groups(self):
        """
        Test `save_groups` with no groups to save.

        :assert: ValueError is raised when no groups are provided.
        """
        logger = MagicMock()
        with self.assertRaises(ValueError):
            save_groups([], "output", logger)


if __name__ == "__main__":
    unittest.main()
